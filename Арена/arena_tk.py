import tkinter as tk
import random
import arena  # твой движок

CELL = 40
DELAY = 200  # мс между кадрами

class ArenaGUI:
    def __init__(self, root, botA, botB):
        self.root = root
        self.botA, self.botB = botA, botB
        self.canvas = tk.Canvas(root, width=arena.W*CELL, height=arena.H*CELL, bg="black")
        self.canvas.pack()
        self.btn = tk.Button(root, text="Start Match", command=self.start_match)
        self.btn.pack()

    def start_match(self):
        self.grid = arena.random_map()
        self.posA = arena.place_bot(self.grid)
        self.posB = arena.place_bot(self.grid, {self.posA})
        self.scoreA = self.scoreB = 0
        self.turn = 0
        self.update_frame()

    def update_frame(self):
        self.turn += 1
        if self.turn > arena.TURNS:
            self.root.title(f"Итог: A={self.scoreA} B={self.scoreB}")
            return

        arena.spawn_food(self.grid)
        obsA = arena.make_observation(self.grid, self.posA, self.posB, self.scoreA, self.scoreB, self.turn)
        obsB = arena.make_observation(self.grid, self.posB, self.posA, self.scoreB, self.scoreA, self.turn)
        actA = self.botA(obsA)
        actB = self.botB(obsB)

        newPosA, _ = arena.step(self.posA, actA if actA != "PICK" else "STAY", self.grid)
        newPosB, _ = arena.step(self.posB, actB if actB != "PICK" else "STAY", self.grid)
        if newPosA == newPosB:
            newPosA, newPosB = self.posA, self.posB
        self.posA, self.posB = newPosA, newPosB

        _, gainA = arena.step(self.posA, actA, self.grid)
        _, gainB = arena.step(self.posB, actB, self.grid)
        self.scoreA += gainA
        self.scoreB += gainB

        self.draw()
        self.root.after(DELAY, self.update_frame)

    def draw(self):
        self.canvas.delete("all")
        for r in range(arena.H):
            for c in range(arena.W):
                x0, y0 = c*CELL, r*CELL
                x1, y1 = x0+CELL, y0+CELL
                if self.grid[r][c] == arena.CellWall:
                    self.canvas.create_rectangle(x0,y0,x1,y1, fill="gray")
                elif self.grid[r][c] == arena.CellFood:
                    self.canvas.create_oval(x0+10,y0+10,x1-10,y1-10, fill="yellow")
        # боты
        self.canvas.create_oval(self.posA[1]*CELL+5, self.posA[0]*CELL+5,
                                self.posA[1]*CELL+CELL-5, self.posA[0]*CELL+CELL-5,
                                fill="cyan")
        self.canvas.create_oval(self.posB[1]*CELL+5, self.posB[0]*CELL+5,
                                self.posB[1]*CELL+CELL-5, self.posB[0]*CELL+CELL-5,
                                fill="red")
        self.root.title(f"Turn {self.turn} | A={self.scoreA} B={self.scoreB}")

if __name__ == "__main__":
    root = tk.Tk()
    gui = ArenaGUI(root, arena.smart_bot_decide, arena.greedy_bot_decide)
    root.mainloop()
