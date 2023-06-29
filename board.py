from random import randrange
import tkinter as tk
from tkinter import ttk

class Board(ttk.Frame):
    """
    The Board class define a single game board with specific number of rows, columns & mines. Each board has 2
    initializations: First the GUI initialization, in which the board parameters assigned and a grid of cells (defined
    as ttk.Labels) are formed and placed. Second initialization happened after the first click of a user on any cell,
    which set the mines location, binds all cells to the user actions.
    """
    # define the labels colors for neighboring hint
    COLORS = (None, 'blue', 'green', 'red', 'purple', 'brown', 'cyan', 'black', 'gray')

    def __init__(self, rows: int, columns: int, n_mines: int, master: tk.Tk = None):
        super(Board, self).__init__(master)
        self.rows = rows
        self.columns = columns
        self.n_mines = n_mines
        self.mines_locs = []
        self.cells = []

        for row in range(rows):
            for column in range(columns):
                cell = ttk.Label(self, width=3, relief='raise', anchor='center', padding=2)
                cell.grid(row=row, column=column)
                cell.bind('<Button-1>', lambda event: self.start(event.widget))
                self.cells.append(cell)

    def cell2loc(self, cell: ttk.Label) -> tuple[int, int]:
        """
        Helper method to convert a widget (Label on the board) to its position, in format of (row, column)
        """
        index = self.cells.index(cell)
        return index // self.columns, index % self.columns

    def loc2cell(self, loc: tuple[int, int]) -> ttk.Label:
        """
        Helper method to convert a position, in format of (row, column), to the corresponding widget
        (Label) on the board
        """
        return self.cells[loc[0] * self.columns + loc[1]]

    def neighbors_loc(self, loc: tuple[int, int]) -> set:
        """
        Helper methods that get a position of a cell on the board, and return a set of the surrounding cells, not
        included the initial position

        :return: set of neighbors positions.
        """
        neighbors = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_row = min(max(loc[0] + i, 0), self.rows - 1)
                neighbor_column = min(max(loc[1] + j, 0), self.columns - 1)
                neighbors.add((neighbor_row, neighbor_column))
        neighbors.discard(loc)
        return neighbors

    def flag(self, cell: ttk.Label) -> None:
        """
        Flag or de-flag cell. Flagged cell cannot be opened without de-flag it first. Flagging are bind only to closed
        cells.
        """
        if str(cell.cget('relief')) == 'raise':
            if not cell.instate(['disabled']):
                cell.configure(state='disabled', text='¶', foreground='red')
                self.master.flags.set(self.master.flags.get() + 1)
            else:
                cell.configure(state='classic', text='')
                self.master.flags.set(self.master.flags.get() - 1)

    def lose(self) -> None:
        """
        End the game with a lose & uncover the hidden mines.
        """
        for mine_loc in self.mines_locs:
            self.loc2cell(mine_loc).configure(text='*', foreground='black')
        self.master.over()

    def win(self) -> bool:
        """
        check if the game over with a win, and return the outcome
        """
        for cell in filter(lambda w: str(w.cget('relief')) == 'raise', self.cells):
            if self.cell2loc(cell) not in self.mines_locs:
                return False
        return True

    def start(self, cell_0: ttk.Label) -> None:
        """
        Initialize the mine locations and the user actions, start the game clock and open the first cell
        """
        loc = self.cell2loc(cell_0)
        while len(self.mines_locs) < self.n_mines:
            row = randrange(self.rows)
            column = randrange(self.columns)
            if (row, column) == loc or (row, column) in self.mines_locs:
                continue
            self.mines_locs.append((row, column))

        for cell in self.cells:
            cell.unbind('<Button-1>')
            cell.bind('<Button-1>', lambda event: self.onclick(event.widget))
            cell.bind('<Button-2>', lambda event: self.flag(event.widget))
            cell.bind('<Button-3>', lambda event: self.flag(event.widget))
        self.master.tic()
        self.onclick(cell_0)

    def onclick(self, cell: ttk.Label):
        """
        Main action of user. By clicking a cell, the game will be end in a lose/win, or be continued. If the game isn't
        over, the cell will exhibit the number of mines that surrounding it. If no mines surround this cell, the game
        will open recursively all the closed neighbors of this cell.
        """
        # work only closed cell
        if not cell.instate(['disabled']):
            cell.configure(relief='flat', state='disabled')

            loc = self.cell2loc(cell)
            # a lose
            if loc in self.mines_locs:
                self.lose()
            else:
                neighbors = self.neighbors_loc(loc)
                # number of neighboring mines
                mines_neighbors = len(neighbors.intersection(self.mines_locs))
                cell.configure(text=mines_neighbors if mines_neighbors else '', foreground=self.COLORS[mines_neighbors])
                # open the neighbor cells recursively
                if mines_neighbors == 0:
                    for neighbor in neighbors:
                        try:
                            # recursion bug in challenge mode: the python interpreter still running although the Tcl
                            # interpreter kill the board. We wrap this with try-except block - which is a valid solution
                            # for this kind of problems.
                            self.onclick(self.loc2cell(neighbor))
                        except tk.TclError:
                            return
            # a win
            if self.win():
                self.master.over()
