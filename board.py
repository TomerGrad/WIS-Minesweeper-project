from random import randrange
import tkinter as tk
from tkinter import ttk

class Board(ttk.Frame):
    """
    The game
    """

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
                cell = ttk.Label(self, width=3, relief='raise', anchor='center')
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
        Helper methods that get a position of a cell on the board, and return a set of the surrounding cells, disclusive
        the initial position

        Examples
        -------
        >>>board = Board(9, 9 ,10)
        >>>board.neighbors_loc((3, 3))
        {(2, 2), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 3), (4, 4)}
        >>> board.neighbors_loc((0, 0))
        {(0, 1), (1, 0), (1, 1)}
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
        if str(cell.cget('relief')) == 'raise':
            if not cell.instate(['disabled']):
                cell.configure(state='disabled', text='¶', foreground='red')
                self.master.flags.set(self.master.flags.get() + 1)
            else:
                cell.configure(state='normal', text='')
                self.master.flags.set(self.master.flags.get() - 1)

    def lose(self):
        for mine_loc in self.mines_locs:
            self.loc2cell(mine_loc).configure(text='*', foreground='black')

    def win(self) -> bool:
        for cell in filter(lambda w: str(w.cget('relief')) == 'raise', self.cells):
            if self.cell2loc(cell) not in self.mines_locs:
                return False
        return True

    def start(self, cell_0: ttk.Label) -> None:
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
        if not cell.instate(['disabled']):
            cell.configure(relief='flat', state='disabled')

            loc = self.cell2loc(cell)
            if loc in self.mines_locs:
                self.lose()
                self.master.over()
            else:
                neighbors = self.neighbors_loc(loc)
                mines_neighbors = len(neighbors.intersection(self.mines_locs))
                cell.configure(text=mines_neighbors if mines_neighbors else '', foreground=self.COLORS[mines_neighbors])
                if mines_neighbors == 0:
                    for neighbor in neighbors:
                        try:
                            # recursion bug in challenge mode: the python interpreter still running although the Tcl
                            # interpreter kill the board. We wrap this with try-except block - which is a valid solution
                            # for this kind of problems.
                            self.onclick(self.loc2cell(neighbor))
                        except tk.TclError:
                            return

            if self.win():
                self.master.over()
