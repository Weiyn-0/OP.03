import tkinter as tk
import random
from time import time


class MinesweeperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Сапёр")
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

        self.create_menu()
        self.create_timer()
        self.show_menu_window()
        

    def create_menu(self):
        menubar = tk.Menu(self.root)

        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Новая игра", command=self.restart)
        game_menu.add_command(label="5 мин", command=lambda: self.set_difficulty(5))
        game_menu.add_command(label="10 мин", command=lambda: self.set_difficulty(10))
        game_menu.add_command(label="15 мин", command=lambda: self.set_difficulty(15))

        menubar.add_cascade(label="Игра", menu=game_menu)
        self.root.config(menu=menubar)

    def set_difficulty(self, bombs):
        self.bomb_count = bombs
        self.restart()


    def create_timer(self):
        self.timer_label = tk.Label(
            self.root,
            text="Время: 0",
            bg="#0A2736",
            fg="white"
        )
        self.timer_label.grid(row=0, column=0, columnspan=self.SIZE)

    def start_timer(self):
        self.game_started = True
        self.start_time = time()
        self.update_timer()

    def update_timer(self):
        if self.game_started:
            seconds = int(time() - self.start_time)
            self.timer_label.config(text=f"Время: {seconds}")
            self.root.after(1000, self.update_timer)

    
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

        return map_mines

    
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

    def get_cell_color(self, i, j):
        return "#8FC07C" if (i + j) % 2 == 0 else "#DEE693"

    def on_click(self, x, y):
        if self.player_map[x][y] != '-' or (x, y) in self.flags:
            return

        if self.first_click:
            self.hidden_map = self.Generator_Map(self.bomb_count, (x, y))
            self.first_click = False
            self.start_timer()

        if self.hidden_map[x + 1][y + 1] == 'M':
            self.buttons[(x, y)].config(text='💣', bg="red")
            self.reveal_all()
            self.game_over()
            return

        self.reveal_cells(x, y)
        self.update_buttons()
        self.check_win()

    def on_right_click(self, x, y):
        if self.player_map[x][y] != '-':
            return

        if (x, y) in self.flags:
            self.flags.remove((x, y))
            self.buttons[(x, y)].config(text='', bg=self.get_cell_color(x, y))
        else:
            self.flags.add((x, y))
            self.buttons[(x, y)].config(text='🚩', bg="#18656A")

    def reveal_cells(self, x, y):
        if not (0 <= x < self.SIZE and 0 <= y < self.SIZE) or self.player_map[x][y] != '-':
            return

        self.player_map[x][y] = self.hidden_map[x + 1][y + 1]

        if self.player_map[x][y] == ' ':
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    self.reveal_cells(x + dx, y + dy)

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

    def reveal_all(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.hidden_map[i + 1][j + 1] == 'M':
                    self.buttons[(i, j)].config(text='💣', bg="#18656A")

    def check_win(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.player_map[i][j] == '-' and self.hidden_map[i + 1][j + 1] != 'M':
                    return
        self.game_win()


    def game_over(self):
        self.game_started = False
        for btn in self.buttons.values():
            btn.config(state='disabled')
        self.show_game_over()

    def game_win(self):
        self.game_started = False
        for btn in self.buttons.values():
            btn.config(state='disabled')


    def restart(self):
        for btn in self.buttons.values():
            btn.destroy()

        self.buttons.clear()
        self.flags.clear()
        self.hidden_map = None
        self.first_click = True
        self.game_started = False

        self.main()

    def show_menu_window(self):
        menu = tk.Toplevel(self.root)
        menu.title("Меню")
        menu.configure(bg="#0A2736")

        tk.Label(menu, text="САПЁР",
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

    def start_game_from_menu(self, menu, bombs):
         self.bomb_count = bombs
         menu.destroy()
         self.restart()

    def show_game_over(self):
         win = tk.Toplevel(self.root)
         win.title("Проигрыш")
         win.configure(bg="#0A2736")

         tk.Label(win, text="Вы проиграли",
             bg="#0A2736", fg="white").pack(pady=10)

         tk.Button(win, text="Заново",
              bg="#18656A", fg="white",
              command=lambda: [win.destroy(), self.restart()]).pack(pady=5)

         win.grab_set()


if __name__ == "__main__":
    root = tk.Tk()
    game = MinesweeperGUI(root)
    root.mainloop()
 