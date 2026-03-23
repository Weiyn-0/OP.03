import tkinter as tk
import random

www = tk.Tk()
www.title("Сапёр")
www.geometry("500x550")
www.configure(bg="#0A2736")

SIZE = 9

scores = {
    5: [],
    10: [],
    15: []
}
buttons = {}
flags = set()
player_map = []
hidden_map = None
display_map = []
first_click = True
bomb_count = 10



def Generator_Map(mines, first_move):
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

def show_menu():
    menu = tk.Toplevel(www)
    menu.title("Меню")
    menu.configure(bg="#0A2736")

    tk.Label(menu, text="САПЁР",
             font=("Arial", 18),
             bg="#0A2736",
             fg="white").pack(pady=10)

    tk.Button(menu, text="Лёгкий (5 мин)",
              bg="#18656A", fg="white",
              command=lambda: start_with_difficulty(menu, 5)).pack(pady=5)

    tk.Button(menu, text="Средний (10 мин)",
              bg="#18656A", fg="white",
              command=lambda: start_with_difficulty(menu, 10)).pack(pady=5)

    tk.Button(menu, text="Сложный (15 мин)",
              bg="#18656A", fg="white",
              command=lambda: start_with_difficulty(menu, 15)).pack(pady=5)

    tk.Button(menu, text="Рейтинг",
              bg="#18656A", fg="white",
              command=show_scores).pack(pady=10)

def start_with_difficulty(menu, bombs):
    global bomb_count

    bomb_count = bombs
    menu.destroy()
    restart()

def reveal_cells(map, player_map, display_map, x, y, size):
    if not (0 <= x < size and 0 <= y < size) or player_map[x][y] != '-':
        return

    player_map[x][y] = map[x + 1][y + 1]
    display_map[x + 1][y + 1] = player_map[x][y]

    if player_map[x][y] == ' ':
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                reveal_cells(map, player_map, display_map, x + dx, y + dy, size)


def get_cell_color(i, j):
    return "#8FC07C" if (i + j) % 2 == 0 else "#DEE693"


def update_buttons():
    for i in range(SIZE):
        for j in range(SIZE):
            val = player_map[i][j]
            if val != '-':
                buttons[(i, j)].config(
                    text=val,
                    relief=tk.SUNKEN,
                    bg=get_cell_color(i, j)
                )


def reveal_all():
    for i in range(SIZE):
        for j in range(SIZE):
            if hidden_map[i + 1][j + 1] == 'M':
                buttons[(i, j)].config(text='💣', bg="#18656A")


def on_click(x, y):
    global hidden_map, first_click

    if player_map[x][y] != '-' or (x, y) in flags:
        return

    if first_click:
        hidden_map = Generator_Map(bomb_count, (x, y))
        first_click = False

    if hidden_map[x + 1][y + 1] == 'M':
        buttons[(x, y)].config(text='💣', bg="red")
        reveal_all()
        show_game_over()
        return

    reveal_cells(hidden_map, player_map, display_map, x, y, SIZE)
    update_buttons()
    check_win()


def on_right_click(x, y):
    if player_map[x][y] != '-':
        return

    if (x, y) in flags:
        flags.remove((x, y))
        buttons[(x, y)].config(text='', bg=get_cell_color(x, y))
    else:
        flags.add((x, y))
        buttons[(x, y)].config(text='🚩', bg="#18656A")


def show_game_over():
    win = tk.Toplevel(www)
    win.title("Проигрыш")
    win.configure(bg="#0A2736")

    tk.Label(win, text="Вы проиграли 💣", bg="#0A2736", fg="white").pack(pady=10)
    tk.Button(win, text="Заново", bg="#18656A", fg="white",
              command=restart).pack(pady=5)

def show_scores():
    win = tk.Toplevel(www)
    win.title("Рейтинг")
    win.configure(bg="#0A2736")

    tk.Label(win, text="Лучшие результаты",
             bg="#0A2736", fg="white",
             font=("Arial", 14)).pack(pady=10)

    for level, times in scores.items():
        text = f"{level} мин: "

        if times:
            best = sorted(times)[:3]
            text += ", ".join(str(t) for t in best)
        else:
            text += "нет результатов"

        tk.Label(win, text=text,
                 bg="#0A2736", fg="white").pack()

def show_win():
    scores[bomb_count].append(seconds)
    win = tk.Toplevel(www)
    win.title("Победа")
    win.configure(bg="#0A2736")

    tk.Label(win, text="Вы победили 🎉", bg="#0A2736", fg="white").pack(pady=10)
    tk.Button(win, text="Заново", bg="#18656A", fg="white",
              command=restart).pack(pady=5)
   
def check_win():
    for i in range(SIZE):
        for j in range(SIZE):
            if player_map[i][j] == '-' and hidden_map[i + 1][j + 1] != 'M':
                return
    show_win()


def restart():
    global player_map, hidden_map, flags, first_click

    for btn in buttons.values():
        btn.destroy()

    buttons.clear()
    flags.clear()
    hidden_map = None
    first_click = True



def main():
    for btn in buttons.values():
        btn.destroy() 
    buttons.clear()


    global player_map, display_map

    player_map = [['-' for _ in range(9)] for _ in range(9)]

    display_map = []
    display_map.append([' '] + list(range(1, 10)))
    for i in range(9):
        display_map.append([i + 1] + player_map[i])

    for i in range(SIZE):
        for j in range(SIZE):
            btn = tk.Button(
                www,
                width=4,
                height=2,
                bg=get_cell_color(i, j),
                fg="black",
                command=lambda x=i, y=j: on_click(x, y)
            )

            btn.grid(row=i, column=j, padx=1, pady=1)

            btn.bind("<Button-3>",
                     lambda e, x=i, y=j: on_right_click(x, y))

            buttons[(i, j)] = btn


main()
show_menu()
www.mainloop()