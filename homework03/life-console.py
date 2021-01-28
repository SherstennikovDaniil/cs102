import curses
import pathlib

import life
from ui import UI


class Console(UI):
    def __init__(self, game: life.GameOfLife) -> None:
        super().__init__(game)
        self.rows = len(self.life.curr_generation)
        self.cols = len(self.life.curr_generation[0])

    def draw_borders(self, screen) -> None:
        screen.border()

    def draw_grid(self, screen) -> None:
        for i in range(1, self.rows - 1):
            for j in range(1, self.cols - 1):
                symbol = "*" if self.life.is_alive((i, j)) else " "
                screen.addch(i, j, symbol)

    def run(self) -> None:
        term = curses.initscr()
        screen = term.derwin(self.rows, self.cols, 0, 0)
        term.keypad(True)
        curses.noecho()
        term.nodelay(True)

        key = ""
        pause = False
        finished = False
        while not pause or not finished:
            try:
                key = chr(term.getch())
                if key == " ":
                    pause = True
                elif key == "q":
                    finished = True
                elif key == "s":
                    self.life.save(pathlib.Path("save.txt"))
                else:
                    pass
            except ValueError:
                pass
            self.draw_borders(screen)
            self.draw_grid(screen)
            screen.refresh()
            self.life.step()
            if self.life.is_changing or not self.life.is_max_generations_exceeded:
                finished = True
        while pause or not finished:
            try:
                key = chr(term.getch())
                if key == " ":
                    pause = False
                elif key == "q":
                    finished = True
                else:
                    pass
            except ValueError:
                pass
        curses.endwin()


if __name__ == "__main__":
    args = life.get_args()
    game_instance = life.GameOfLife((args.rows, args.rows), max_generations=args.max_gens)
    if args.load_path:
        game_instance = game_instance.from_file(args.load_path)
    ui = Console(game_instance)
    ui.run()
