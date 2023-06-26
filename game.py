import json
from time import gmtime, strftime
import tkinter as tk
from tkinter import ttk

from board import Board
from info import Fame, helper


class Game(tk.Tk):

    LEVELS = {'easy': dict(rows=9, columns=9, n_mines=10),
              'normal': dict(rows=16, columns=16, n_mines=40),
              'hard': dict(rows=16, columns=36, n_mines=99)}

    CHALLENGE = {'easy': dict(time=900, t_decrease=5, t_limit=300, d_mines=2, score=-1),
                 'normal': dict(time=600, t_decrease=5, t_limit=240, d_mines=1, score=-1),
                 'hard': dict(time=600, t_decrease=6, t_limit=180, d_mines=1, score=-1)}

    def __init__(self):
        super(Game, self).__init__()
        self.resizable(False, False)
        self.title('Our MineSweeper')
        self.style = ttk.Style()

        self.tac = None
        self.time = None
        self.board = None

        self.clock = tk.StringVar(self, value='Click to play')
        self.mines = tk.IntVar(self)
        self.flags = tk.IntVar(self)
        self.mode = tk.StringVar(self)
        self.level = tk.StringVar(self)
        self.theme = tk.StringVar(self)

        try:
            with open('options.json') as fp:
                options = json.load(fp)
        except FileNotFoundError:
            options = dict(level='easy', mode='normal', theme='classic')

        self.level.set(options['level'])
        self.mode.set(options['mode'])
        self.theme.set(options['theme'])
        self.set_theme()
        self.board_params = self.LEVELS[options['level']].copy()
        self.challenge_params = self.CHALLENGE[options['level']].copy()

        self.fame = Fame(self)          # add yours filename if you want another json record file

        self.menu_and_panels()

        # add keyboard shortcuts
        self.bind('<Control-n>', lambda event: self.new_game())
        self.bind('<Control-h>', lambda event: helper(self))
        self.bind('<Control-f>', lambda event: self.fame.show())
        self.bind('<Escape>', lambda event: self.destroy())

        self.new_game()

    def menu_and_panels(self):
        # menus #
        self.option_add('*tearOff', False)
        main_menu = tk.Menu(self)

        # control menu: new game and level and mode controllers
        control_menu = tk.Menu(main_menu)
        level_menu = tk.Menu(control_menu)
        mode_menu = tk.Menu(control_menu)

        level_menu.add_radiobutton(label='Easy', variable=self.level, value='easy', command=self.new_game)
        level_menu.add_radiobutton(label='Normal', variable=self.level, value='normal', command=self.new_game)
        level_menu.add_radiobutton(label='Hard', variable=self.level, value='hard', command=self.new_game)

        mode_menu.add_radiobutton(label='Normal', variable=self.mode, value='normal', command=self.new_game)
        mode_menu.add_radiobutton(label='Challenge', variable=self.mode, value='challenge', command=self.new_game)

        control_menu.add_command(label='New', accelerator='Ctrl-N', command=self.new_game)
        control_menu.add_separator()
        control_menu.add_cascade(label='Level', menu=level_menu)
        control_menu.add_cascade(label='Mode', menu=mode_menu)
        control_menu.add_separator()
        control_menu.add_command(label='Close', accelerator='Esc', command=self.destroy)
        main_menu.add_cascade(label='Control', menu=control_menu)

        # info menu: hall of fame and help
        info_menu = tk.Menu(main_menu)
        info_menu.add_command(label='Hall of Fame', accelerator='Ctrl-F', command=self.fame.show)
        info_menu.add_command(label='Help', accelerator='Ctrl-H', command=lambda: helper(self))
        info_menu.add_separator()
        info_menu.add_command(label='Reset', command=self.fame.reset)
        main_menu.add_cascade(label='Info', menu=info_menu)

        # themes menu: appearance change
        theme_menu = tk.Menu(main_menu)
        for theme in self.style.theme_names():
            theme_menu.add_radiobutton(label=theme, value=theme, variable=self.theme, command=self.set_theme)
        main_menu.add_cascade(label='Theme', menu=theme_menu)

        self.configure(menu=main_menu)

        # Upper control panel with the game-time label and the mode info
        upper = ttk.Frame(self, relief='raise', borderwidth=2)
        ttk.Label(upper, textvariable=self.clock).pack(side='left')
        ttk.Label(upper, textvariable=self.mode).pack(side='right')
        ttk.Label(upper, text='Mode:').pack(side='right')
        upper.grid(row=0, sticky=('e', 'w'))

        # bottom panel help to be in control on the hidden mines and the marked flags
        bottom = ttk.Frame(self, relief='raise', borderwidth=2)
        ttk.Label(bottom, text='Flags: ').pack(side='left')
        ttk.Label(bottom, textvariable=self.flags).pack(side='left')
        ttk.Label(bottom, textvariable=self.mines).pack(side='right')
        ttk.Label(bottom, text='Mines: ').pack(side='right')
        bottom.grid(row=2, sticky=('e', 'w'))

    def set_theme(self):
        self.style.theme_use(self.theme.get())

    def tic(self):
        self.detic()
        self.clock.set(strftime("%H:%M:%S", gmtime(self.time)))
        if self.mode.get() == 'normal':
            self.time += 1
        else:
            self.time -= 1
            if self.time < 0:
                self.over()
        self.tac = self.after(1000, self.tic)

    def detic(self):
        if self.tac:
            self.after_cancel(self.tac)

    def over(self):
        is_challenge = self.mode.get() == 'challenge'
        is_win = self.board.win()

        if is_challenge and is_win:
            self.challenge()
        else:
            self.detic()
            for cell in self.board.winfo_children():
                cell.unbind('<Button-1>')
                cell.unbind('<Button-2>')
                cell.unbind('<Button-3>')

            current_record = self.fame.records[self.mode.get()][self.level.get()]
            if not is_challenge and is_win:
                if current_record is None or self.time < current_record[1]:
                    self.fame.update(self.time)
                    self.fame.show()
            elif is_challenge and not is_win:
                if current_record is None or self.challenge_params['score'] > current_record[1]:
                    self.fame.update(self.challenge_params['score'])
                    self.fame.show()

            self.clock.set('Click to replay')
            self.bind('<Button-1>', lambda event: self.new_game())

    def normal(self):
        self.time = 0
        self.flags.set(0)
        self.board = Board(self, **self.board_params)
        self.mines.set(self.board_params['n_mines'])
        self.board.grid(row=1)

    def challenge(self):
        if self.board is not None:
            self.board.destroy()

        self.time = self.challenge_params['time']
        self.flags.set(0)
        self.mines.set(self.board_params['n_mines'])
        self.board = Board(self, **self.board_params)

        if self.challenge_params['time'] > self.challenge_params['t_limit']:
            self.challenge_params['time'] -= self.challenge_params['t_decrease']

        if not self.challenge_params['score'] % self.challenge_params['d_mines']:
            self.board_params['n_mines'] += 1

        if not self.challenge_params['score'] % (self.challenge_params['d_mines'] * 4):
            self.board_params['rows'] += 1
        elif not self.challenge_params['score'] % (self.challenge_params['d_mines'] * 2):
            self.board_params['columns'] += 1
        self.challenge_params['score'] += 1
        self.board.grid(row=1)

    def new_game(self):
        try:
            self.board.destroy()
            self.detic()
        except AttributeError:
            pass
        finally:
            self.unbind('<Button-1>')
            self.board_params = self.LEVELS[self.level.get()].copy()
            self.challenge_params = self.CHALLENGE[self.level.get()].copy()
            if self.mode.get() == 'normal':
                self.normal()
            else:
                self.challenge()
            self.clock.set('Click to play')
    
    def destroy(self):
        with open('options.json', 'w') as fp:
            json.dump(dict(mode=self.mode.get(), level=self.level.get(), theme=self.theme.get()), fp)
        self.fame.save()        # add yours filename if you want another json record file
        super(Game, self).destroy()


if __name__ == '__main__':
    Game().mainloop()
