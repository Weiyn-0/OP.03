import tkinter as tk
import random
from time import time
import logging


logging.basicConfig(
    filename="game.log", 
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger("Minesweeper")


def log_method(func):
    def wrapper(self, *args, **kwargs):
        method_name = func.__name__
        
        args_str = ", ".join([str(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        
        if args_str and kwargs_str:
            all_args = f"{args_str}, {kwargs_str}"
        elif args_str:
            all_args = args_str
        elif kwargs_str:
            all_args = kwargs_str
        else:
            all_args = ""
        
        logger.info(f"Вызов метода: {method_name}({all_args})")
        
        try:
            result = func(self, *args, **kwargs)
            
            if result is not None:
                logger.debug(f"Метод {method_name} вернул: {result}")
            else:
                logger.debug(f"Метод {method_name} успешно")
            
            return result
            
        except Exception as e:
            logger.error(f"услышал тебя родной: {method_name}: {e}", exc_info=True)
            raise
    
    wrapper.__name__ = func.__name__
    return wrapper


class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Полянка несмеянка")
        self.root.geometry("500x550")
        self.root.configure(bg="#0A2736")

        self.SIZE = 9
        self.bomb_count = 10

        self.buttons = {}
        self.flags = set()
        self.player_map = []
        self.hidden_map = None
        self.first_click = True

        self.game_started = False
        self.start_time = 0
        
        
        self.clicks_count = 0
        self.flag_count = 0
        self.game_count = 0

        logger.info("Полянка несмеянка инициализируется")
        self.create_menu()
        self.create_timer()
        self.show_menu_window()
    
    @log_method
    def create_menu(self):
        menubar = tk.Menu(self.root)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.restart)
        game_menu.add_command(label="5 мин", command=lambda: self.set_difficulty(5))
        game_menu.add_command(label="10 мин", command=lambda: self.set_difficulty(10))
        game_menu.add_command(label="15 мин", command=lambda: self.set_difficulty(15))

        menubar.add_cascade(label="Игра", menu=game_menu)
        self.root.config(menu=menubar)
    
    @log_method
    def set_difficulty(self, bombs):
        logger.info(f"А можно другую сложность???: {bombs} мин")
        self.bomb_count = bombs
        self.restart()
    
    @log_method
    def create_timer(self):
        self.timer_label = tk.Label(
            self.root,
            text="Время: 0",
            bg="#0A2736",
            fg="white"
        )
        self.timer_label.grid(row=0, column=0, columnspan=self.SIZE)
    
    @log_method
    def start_timer(self):
        self.game_started = True
        self.start_time = time()
        self.update_timer()
        logger.info("Таймер запущен")
    
    @log_method
    def update_timer(self):
        if self.game_started:
            seconds = int(time() - self.start_time)
            self.timer_label.config(text=f"Время: {seconds}")
            self.root.after(1000, self.update_timer)
    
    @log_method
    def Generator_Map(self, mines, first_move):
        size = 9
        map_dict = {}

        mines_count = mines
        mines = set()
        first_x, first_y = first_move

        while len(mines) < mines_count:
            x, y = random.randint(0, size - 1), random.randint(0, size - 1)
            if (x, y) != (first_x, first_y):
                mines.add((x, y))
                map_dict[(x, y)] = 'M'

        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for x in range(size):
            for y in range(size):
                if (x, y) not in map_dict:
                    count = 0
                    for dx, dy in directions:
                        if (x + dx, y + dy) in map_dict:
                            count += 1
                    map_dict[(x, y)] = str(count) if count > 0 else ' '

        map_mines = [[' '] + list(range(1, size + 1))]
        for i in range(size):
            row = [i + 1]
            for j in range(size):
                row.append(map_dict.get((i, j), ' '))
            map_mines.append(row)
        
        logger.info(f"Картаа с {mines_count} минами, 1 клик: {first_move}")
        return map_mines
    
    @log_method
    def main(self):
        self.player_map = [['-' for _ in range(9)] for _ in range(9)]

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                btn = tk.Button(
                    self.root,
                    width=4,
                    height=2,
                    bg=self.get_cell_color(i, j),
                    command=lambda x=i, y=j: self.on_click(x, y)
                )

                btn.grid(row=i + 1, column=j)
                btn.bind("<Button-3>", lambda e, x=i, y=j: self.on_right_click(x, y))

                self.buttons[(i, j)] = btn
        
        logger.info("Игр. поле создано")
    
    @log_method
    def get_cell_color(self, i, j):
        return "#8FC07C" if (i + j) % 2 == 0 else "#DEE693"
    
    @log_method
    def on_click(self, x, y):
        self.clicks_count += 1
        logger.info(f"по клетке ({x}, {y}), все клики: {self.clicks_count}")
        
        if self.player_map[x][y] != '-' or (x, y) in self.flags:
            logger.debug(f"Кинут в игнор на клетке статус открыта или под флагом")
            return

        if self.first_click:
            logger.info("Для начала")
            self.hidden_map = self.Generator_Map(self.bomb_count, (x, y))
            self.first_click = False
            self.start_timer()

        if self.hidden_map[x + 1][y + 1] == 'M':
            logger.warning(f"Игрока разнесло на пару километров({x}, {y})")
            self.buttons[(x, y)].config(text='💣', bg="red")
            self.reveal_all()
            self.game_over()
            return

        self.reveal_cells(x, y)
        self.update_buttons()
        self.check_win()
    
    @log_method
    def on_right_click(self, x, y):
        logger.info(f"Right клик по клетке ({x}, {y})")
        
        if self.player_map[x][y] != '-':
            logger.debug(f"Зачем кликает, непонятно. Вывод: дурак")
            return

        if (x, y) in self.flags:
            self.flags.remove((x, y))
            self.flag_count -= 1
            self.buttons[(x, y)].config(text='', bg=self.get_cell_color(x, y))
            logger.info(f"Флаг снят с ({x}, {y}), осталось флаг: {self.flag_count}")
        else:
            self.flags.add((x, y))
            self.flag_count += 1
            self.buttons[(x, y)].config(text='🚩', bg="#18656A")
            logger.info(f"Флаг на клетке ({x}, {y}), всего флагов: {self.flag_count}")
    
    @log_method
    def reveal_cells(self, x, y):
        if not (0 <= x < self.SIZE and 0 <= y < self.SIZE) or self.player_map[x][y] != '-':
            return

        self.player_map[x][y] = self.hidden_map[x + 1][y + 1]
        if self.player_map[x][y] == ' ':
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    self.reveal_cells(x + dx, y + dy)
    
    @log_method
    def update_buttons(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                val = self.player_map[i][j]
                if val != '-':
                    self.buttons[(i, j)].config(
                        text=val,
                        relief=tk.SUNKEN,
                        bg=self.get_cell_color(i, j)
                    )
    
    @log_method
    def reveal_all(self):
        mine_count = 0
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.hidden_map[i + 1][j + 1] == 'M':
                    self.buttons[(i, j)].config(text='💣', bg="#18656A")
                    mine_count += 1
        logger.info(f"мины: {mine_count}")
    
    @log_method
    def check_win(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.player_map[i][j] == '-' and self.hidden_map[i + 1][j + 1] != 'M':
                    return
        self.game_win()
    
    @log_method
    def game_over(self):
        game_time = int(time() - self.start_time) if self.start_time else 0
        logger.error(f"Для лохов. Статы: клик клац={self.clicks_count}, флаг={self.flag_count}, тик так={game_time}с")
        self.game_started = False
        for btn in self.buttons.values():
            btn.config(state='disabled')
        self.show_game_over()
    
    @log_method
    def game_win(self):
        self.game_count += 1
        game_time = int(time() - self.start_time) if self.start_time else 0
        logger.info(f"Смотрите не лох. СТаты: Лудоманы тоже люди #{self.game_count}, Потраченного времени жаль={game_time}с., Куки кликер крут={self.clicks_count}, ред флааг ={self.flag_count}")
        self.game_started = False
        for btn in self.buttons.values():
            btn.config(state='disabled')
        self.show_game_win()
    
    @log_method
    def restart(self):
        logger.info(f"Рестарт. Пред.стат: клик клац={self.clicks_count}, флаги={self.flag_count}")
        
        for btn in self.buttons.values():
            btn.destroy()

        self.buttons.clear()
        self.flags.clear()
        self.hidden_map = None
        self.first_click = True
        self.game_started = False
        self.clicks_count = 0
        self.flag_count = 0
        self.start_time = 0

        self.main()
        logger.info("Игра перезапущена")
    
    @log_method
    def show_menu_window(self):
        menu = tk.Toplevel(self.root)
        menu.title("Меню")
        menu.configure(bg="#0A2736")

        tk.Label(menu, text="Полянка несмеянка",
             font=("Arial", 18),
             bg="#0A2736",
             fg="white").pack(pady=10)

        tk.Button(menu, text="Лёгкий (5)",
                bg="#18656A", fg="white",
                command=lambda: self.start_game_from_menu(menu, 5)).pack(pady=5)

        tk.Button(menu, text="Средний (10)",
                bg="#18656A", fg="white",
                command=lambda: self.start_game_from_menu(menu, 10)).pack(pady=5)

        tk.Button(menu, text="Сложный (15)",
                bg="#18656A", fg="white",
                command=lambda: self.start_game_from_menu(menu, 15)).pack(pady=5)

        menu.grab_set()
        logger.info("Выбор сложности")
    
    @log_method
    def start_game_from_menu(self, menu, bombs):
        logger.info(f"Взорваться: {bombs} мин")
        self.bomb_count = bombs
        menu.destroy()
        self.restart()
    
    @log_method
    def show_game_over(self):
        win = tk.Toplevel(self.root)
        win.title("Лохопедия")
        win.configure(bg="#0A2736")

        tk.Label(win, text="U're loser",
             bg="#0A2736", fg="white").pack(pady=10)

        tk.Button(win, text="Рестарт",
              bg="#18656A", fg="white",
              command=lambda: [win.destroy(), self.restart()]).pack(pady=5)
        win.grab_set()
    
    @log_method
    def show_game_win(self):
        win = tk.Toplevel(self.root)
        win.title("Изи пизи лаймон сквизи")
        win.configure(bg="#0A2736")

        game_time = int(time() - self.start_time) if self.start_time else 0
        
        tk.Label(win, text="GG",
             font=("Arial", 14),
             bg="#0A2736", fg="gold").pack(pady=10)
        
        tk.Label(win, text=f"Потраченно: {game_time} секунд",
             bg="#0A2736", fg="white").pack(pady=5)
        
        tk.Label(win, text=f"Куки кликер момент: {self.clicks_count}",
             bg="#0A2736", fg="white").pack(pady=5)

        tk.Button(win, text="Ну че, снова?",
              bg="#18656A", fg="white",
              command=lambda: [win.destroy(), self.restart()]).pack(pady=10)

        win.grab_set()


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Программа старт")
    logger.info("Игра запуск")
    logger.info("=" * 50)
    
    root = tk.Tk()
    game = MinesweeperGUI(root)
    root.mainloop()
    
    logger.info("Программа всё")