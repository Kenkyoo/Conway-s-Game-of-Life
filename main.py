import tkinter as tk
import random

# ── Constants ─────────────────────────────────────────────────────────────────
ROWS  = 40
COLS  = 60
SIZE  = 12
WIDTH = COLS * SIZE
HEIGHT = ROWS * SIZE
DELAY = 80

COLOR_DEAD   = "#11111b"
COLOR_GRID   = "#1e1e2e"
COLOR_BG     = "#181825"

# Colors pallete catppuccin mocha
COLORS = {
    "Rosewater": "#f5e0dc",
    "Flamingo":  "#f2cdcd",
    "Pink":      "#f5c2e7",
    "Mauve":     "#cba6f7",
    "Red":       "#f38ba8",
    "Maroon":    "#eba0ac",
    "Peach":     "#fab387",
    "Yellow":    "#f9e2af",
    "Green":     "#a6e3a1",
    "Teal":      "#94e2d5",
    "Sky":       "#89b4fa",
    "Sapphire":  "#74c7ec",
}

# ── Grid ──────────────────────────────────────────────────────────────────────

def create_grid():
    return [[0] * COLS for _ in range(ROWS)]


def count_neighbors(grid, row, col):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r = (row + dr) % ROWS
            c = (col + dc) % COLS
            count += grid[r][c]
    return count


def next_generation(grid):
    new = create_grid()
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = count_neighbors(grid, row, col)
            if grid[row][col] == 1:
                new[row][col] = 1 if neighbors in (2, 3) else 0
            else:
                new[row][col] = 1 if neighbors == 3 else 0
    return new

# ── Predefined patterns ───────────────────────────────────────────────────────

def load_glider(grid):
    grid = create_grid()
    r, c = ROWS // 4, COLS // 4
    pattern = [
        (r,   c+1),
        (r+1, c+2),
        (r+2, c),
        (r+2, c+1),
        (r+2, c+2),
    ]
    for row, col in pattern:
        grid[row][col] = 1
    return grid


def load_pulsar(grid):
    grid = create_grid()
    cr, cc = ROWS // 2 - 6, COLS // 2 - 6
    cells = [
        (0,2),(0,3),(0,4),(0,8),(0,9),(0,10),
        (2,0),(3,0),(4,0),(2,5),(3,5),(4,5),
        (2,7),(3,7),(4,7),(2,12),(3,12),(4,12),
        (5,2),(5,3),(5,4),(5,8),(5,9),(5,10),
        (7,2),(7,3),(7,4),(7,8),(7,9),(7,10),
        (8,0),(9,0),(10,0),(8,5),(9,5),(10,5),
        (8,7),(9,7),(10,7),(8,12),(9,12),(10,12),
        (12,2),(12,3),(12,4),(12,8),(12,9),(12,10),
    ]
    for dr, dc in cells:
        r, c = cr + dr, cc + dc
        if 0 <= r < ROWS and 0 <= c < COLS:
            grid[r][c] = 1
    return grid


def load_random(grid):
    return [[1 if random.random() < 0.3 else 0 for _ in range(COLS)] for _ in range(ROWS)]

def load_blinker(grid):
    r, c = ROWS//2, COLS//2
    for i in range(3):
        grid[r][c+i] = 1
    return grid

def load_toad(grid):
    r, c = ROWS//2, COLS//2
    pattern = [(r, c+1), (r, c+2), (r, c+3),
               (r+1, c), (r+1, c+1), (r+1, c+2)]
    for row, col in pattern:
        grid[row][col] = 1
    return grid

# ── Interface ─────────────────────────────────────────────────────────────────

class GameOfLife:
    def __init__(self, root):
        self.root = root
        self.root.title("Game of Life")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)

        self.grid      = create_grid()
        self.running   = False
        self.job       = None
        self.generation = 0
        self.color_alive = list(COLORS.values())[0]
        self._create_widgets()
        self.draw()

    # ── UI setup ──────────────────────────────────────────────────────────────

    def _create_widgets(self):
        # Title
        title = tk.Label(
            self.root, text="GAME  OF  LIFE",
            bg=COLOR_BG, fg="#f38ba8",
            font=("Courier", 12, "bold"), pady=8
        )
        title.pack()

        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH, height=HEIGHT,
            bg=COLOR_DEAD, highlightthickness=0
        )
        self.canvas.pack(padx=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_click)

        # ── Main ──────────────────────────────────────────────────────────

        self.lbl_gen4 = tk.Label(self.root, text="Main",
                                bg=COLOR_BG, fg="#89b4fa", font=("Courier", 12))
        self.lbl_gen4.pack(pady=(2, 2))

        # Button panel
        panel = tk.Frame(self.root, bg=COLOR_BG, pady=8)
        panel.pack()

        btn_style = dict(
            bg="#cba6f7", fg="#11111b",
            activebackground="#7f849c", activeforeground=self.color_alive,
            relief="flat", font=("Courier", 8, "bold"),
            width=8, pady=2, cursor="hand2"
        )

        self.btn_start = tk.Button(panel, text="▶  Start",
                                   command=self.start, **btn_style)
        self.btn_start.grid(row=2, column=1, padx=4)

        self.btn_pause = tk.Button(panel, text="⏸  Pause",
                                   command=self.pause, **btn_style,
                                   state="disabled")
        self.btn_pause.grid(row=2, column=2, padx=4)

        tk.Button(panel, text="🗑  Clear",
                  command=self.clear, **btn_style).grid(row=2, column=3, padx=4)


        # ── Info ──────────────────────────────────────────────────────────

        self.lbl_gen3 = tk.Label(self.root, text="How to use: First select a pattern, then press start. Done!",
                                bg=COLOR_BG, fg="#a6e3a1", font=("Courier", 8))
        self.lbl_gen3.pack(pady=(2, 8))

        # Pattern label

        tk.Label(panel, text="Patterns:", bg=COLOR_BG, fg="#cdd6f4",
                 font=("Courier", 9)).grid(row=1, column=1, columnspan=3, pady=(8, 2))

        tk.Button(panel, text="✦  Glider",
                  command=self.pattern_glider, **btn_style).grid(row=0, column=0, padx=4)

        tk.Button(panel, text="✦  Pulsar",
                  command=self.pattern_pulsar, **btn_style).grid(row=0, column=1, padx=4)

        tk.Button(panel, text="⁂  Random",
                  command=self.pattern_random, **btn_style).grid(row=0, column=2, padx=4)

        tk.Button(panel, text="⁂  Blinker",
                  command=self.pattern_blinker, **btn_style).grid(row=0, column=3, padx=4)

        tk.Button(panel, text="⁂  Toad",
                  command=self.pattern_load_toad, **btn_style).grid(row=0, column=4, padx=4)

        # ── Color selector ────────────────────────────────────────────────────
        color_frame = tk.Frame(self.root, bg=COLOR_BG, pady=4)
        color_frame.pack()
 
        tk.Label(color_frame, text="Cell color:", bg=COLOR_BG, fg="#cdd6f4",
                 font=("Courier", 9)).pack(side="left", padx=(0, 6))
 
        # Small square showing current color
        self.color_preview = tk.Canvas(color_frame, width=16, height=16,
                                       bg=self.color_alive, highlightthickness=1,
                                       highlightbackground="#444")
        self.color_preview.pack(side="left", padx=(0, 4))
 
        # OptionMenu
        self.selected_color = tk.StringVar(value=list(COLORS.keys())[0])
        self.selected_color.trace("w", self._on_color_change)
 
        menu = tk.OptionMenu(color_frame, self.selected_color, *COLORS.keys())
        menu.config(bg="#1e1e2e", fg="#cdd6f4", activebackground="#333",
                    activeforeground="#cdd6f4", relief="flat",
                    font=("Courier", 9), highlightthickness=0,
                    cursor="hand2", width=12)
        menu["menu"].config(bg="#1e1e2e", fg="#cdd6f4",
                            activebackground="#333", activeforeground="#cdd6f4",
                            font=("Courier", 9))
        menu.pack(side="left")
 
    # ── Generation counter ──────────────────────────────────────────────────────────

        self.lbl_gen = tk.Label(self.root, text="Generation: 0",
                                bg=COLOR_BG, fg="#cdd6f4", font=("Courier", 9))
        self.lbl_gen.pack(pady=(2, 8))


    # ── About ──────────────────────────────────────────────────────────

        self.lbl_gen2 = tk.Label(self.root, text="Made by Kenkyo with a lot of ❤️",
                                bg=COLOR_BG, fg="#f5e0dc", font=("Courier", 9))
        self.lbl_gen2.pack(pady=(2, 8))
 
    # ── Color change ──────────────────────────────────────────────────────────
 
    def _on_color_change(self, *args):
        name = self.selected_color.get()
        self.color_alive = COLORS[name]
        self.color_preview.config(bg=self.color_alive)
        self.draw()

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self):
        self.canvas.delete("all")
        for row in range(ROWS):
            for col in range(COLS):
                x1 = col  * SIZE
                y1 = row  * SIZE
                x2 = x1 + SIZE - 1
                y2 = y1 + SIZE - 1
                color = self.color_alive if self.grid[row][col] else COLOR_DEAD
                self.canvas.create_rectangle(x1, y1, x2, y2,
                                             fill=color, outline=COLOR_GRID, width=1)

    # ── Mouse interaction ─────────────────────────────────────────────────────

    def on_click(self, event):
        col = event.x // SIZE
        row = event.y // SIZE
        if 0 <= row < ROWS and 0 <= col < COLS:
            self.grid[row][col] ^= 1
            self.draw()

    # ── Main loop ─────────────────────────────────────────────────────────────

    def _tick(self):
        self.grid = next_generation(self.grid)
        self.generation += 1
        self.lbl_gen.config(text=f"Generation: {self.generation}")
        self.draw()
        if self.running:
            self.job = self.root.after(DELAY, self._tick)

    # ── Main ─────────────────────────────────────────────────────────────

    def _main(self):
        self.lbl_gen4.config()
        self.draw()
        if self.running:
            self.job = self.root.after(DELAY, self._main)

    # ── About ─────────────────────────────────────────────────────────────

    def _about(self):
        self.lbl_gen2.config()
        self.draw()
        if self.running:
            self.job = self.root.after(DELAY, self._about)

    # ── Info ─────────────────────────────────────────────────────────────

    def _info(self):
        self.lbl_gen3.config()
        self.draw()
        if self.running:
            self.job = self.root.after(DELAY, self._info)

    # ── Buttons ───────────────────────────────────────────────────────────────

    def start(self):
        if not self.running:
            self.running = True
            self.btn_start.config(state="disabled")
            self.btn_pause.config(state="normal")
            self._tick()

    def pause(self):
        self.running = False
        if self.job:
            self.root.after_cancel(self.job)
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled")

    def clear(self):
        self.pause()
        self.grid = create_grid()
        self.generation = 0
        self.lbl_gen.config(text="Generation: 0")
        self.draw()

    def pattern_glider(self):
        self.pause()
        self.grid = load_glider(self.grid)
        self.generation = 0
        self.lbl_gen.config(text="Generation: 0")
        self.draw()

    def pattern_pulsar(self):
        self.pause()
        self.grid = load_pulsar(self.grid)
        self.generation = 0
        self.lbl_gen.config(text="Generation: 0")
        self.draw()

    def pattern_random(self):
        self.pause()
        self.grid = load_random(self.grid)
        self.generation = 0
        self.lbl_gen.config(text="Generation: 0")
        self.draw()

    def pattern_blinker(self):
        self.pause()
        self.grid = load_blinker(self.grid)
        self.generation = 0
        self.lbl_gen.config(text="Generation: 0")
        self.draw()

    def pattern_load_toad(self):
        self.pause()
        self.grid = load_toad(self.grid)
        self.generation = 0
        self.lbl_gen.config(text="Generation: 0")
        self.draw()

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    GameOfLife(root)
    root.mainloop()

if __name__ == "__main__":
    main()