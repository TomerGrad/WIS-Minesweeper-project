import json
from time import gmtime, strftime
import tkinter as tk
from tkinter import ttk

# Want extra themes? you can install ttkthemes package, but it isn't mandatory
try:
    from ttkthemes import ThemedStyle as Style
except ImportError:
    from tkinter.ttk import Style

from board import Board
from info import Fame, helper


class Game(tk.Tk):
    """
    The main game app, which handle all the user setting of game type
    """
    # board params by level
    LEVELS = {'easy': dict(rows=9, columns=9, n_mines=10),
              'normal': dict(rows=16, columns=16, n_mines=40),
              'hard': dict(rows=16, columns=36, n_mines=99)}

    # changes in the board params by level
    CHALLENGE = {'easy': dict(time=900, t_decrease=5, t_limit=300, d_mines=2, score=-1),
                 'normal': dict(time=600, t_decrease=5, t_limit=240, d_mines=1, score=-1),
                 'hard': dict(time=600, t_decrease=6, t_limit=180, d_mines=1, score=-1)}

    def __init__(self):
        super(Game, self).__init__()
        self.resizable(False, False)
        self.title('Our MineSweeper')
        self.style = Style()

        self.tac = None
        self.time = None
        self.board = None

        self.clock = tk.StringVar(self, value='Click to play')
        self.mines = tk.IntVar(self)
        self.flags = tk.IntVar(self)
        self.mode = tk.StringVar(self)
        self.level = tk.StringVar(self)
        self.theme = tk.StringVar(self)

        # load and set the last game played setting
        try:
            with open('setting.json') as fp:
                setting = json.load(fp)
        # if there is any...
        except FileNotFoundError:
            setting = dict(level='easy', mode='classic', theme='classic')
        self.level.set(setting['level'])
        self.mode.set(setting['mode'])
        self.theme.set(setting['theme'])
        self.set_theme()
        self.board_params = self.LEVELS[setting['level']].copy()
        self.challenge_params = self.CHALLENGE[setting['level']].copy()

        self.fame = Fame(self)          # add yours filename if you want another json record file

        # add the control frame of the app
        self.menu_and_panels()

        # add keyboard shortcuts
        self.bind('<Control-n>', lambda event: self.new_game())
        self.bind('<Control-h>', lambda event: helper(self))
        self.bind('<Control-f>', lambda event: self.fame.show())
        self.bind('<Escape>', lambda event: self.destroy())

        # initiate a new game based on the setting
        self.new_game()

    def menu_and_panels(self):
        """
        Builds the menus of game-control, fame and help, and appearance; Builds the panels that shows the time,
        flagged cells and hidden mines of the current game.
        """
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

        mode_menu.add_radiobutton(label='Classic', variable=self.mode, value='classic', command=self.new_game)
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
        # using the built-in themes - may vary as decency on the platform.
        for theme in sorted(self.style.theme_names()):
            theme_menu.add_radiobutton(label=theme, value=theme, variable=self.theme, command=self.set_theme)
        main_menu.add_cascade(label='Themes', menu=theme_menu)

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
        """
        Change the way the app look like
        """
        self.style.theme_use(self.theme.get())

    def tic(self):
        """
        Measure the game time. For 'classic' mode the time is cumulative and represent the score. For 'challenge' mode
        the time is decreasing and if it hit zero the game is over with a lose.
        """
        self.detic()
        self.clock.set(strftime("%H:%M:%S", gmtime(self.time)))
        if self.mode.get() == 'classic':
            self.time += 1
        else:
            self.time -= 1
            if self.time < 0:
                self.over()
        self.tac = self.after(1000, self.tic)

    def detic(self):
        """
        Helper method. cancel the call to Game.tic, so the game could over properly and the app could be closed.
        """
        if self.tac:
            self.after_cancel(self.tac)

    def over(self):
        """
        End of the current game. The method deals with loading new game in win situation challenge mode, and updating
        new records.
        """
        is_challenge = self.mode.get() == 'challenge'
        is_win = self.board.win()

        # play another round
        if is_challenge and is_win:
            self.challenge()
        else:
            self.detic()
            for cell in self.board.winfo_children():
                cell.unbind('<Button-1>')
                cell.unbind('<Button-2>')
                cell.unbind('<Button-3>')

            current_record: dict = self.fame.records[self.mode.get()][self.level.get()]
            # classic mode winner
            if not is_challenge and is_win:
                if not current_record or self.time < min(current_record.values()):
                    self.fame.update(self.time)
                    self.fame.show()
            # race mode winner
            elif is_challenge and not is_win:
                if not current_record or self.challenge_params['score'] > max(current_record.values()):
                    self.fame.update(self.challenge_params['score'])
                    self.fame.show()

            # load a new game with the current mode & level with the player action
            self.clock.set('Click to replay')
            self.bind('<Button-1>', lambda event: self.new_game())

    def classic(self):
        """
        Load the a new classic game.
        """
        self.time = 0
        self.flags.set(0)
        self.board = Board(master=self, **self.board_params)
        self.mines.set(self.board_params['n_mines'])
        self.board.grid(row=1)

    def challenge(self):
        """
        Load our new mode: challenge. By each win, another, harder game will be loaded immediately, and the clock will
        start ticking.
        """
        if self.board is not None:
            self.board.destroy()

        # load the new game
        self.time = self.challenge_params['time']
        self.flags.set(0)
        self.mines.set(self.board_params['n_mines'])
        self.board = Board(master=self, **self.board_params)

        # updating the parameters, so the next game will be harder
        # decrease time (with some limitations)
        if self.challenge_params['time'] > self.challenge_params['t_limit']:
            self.challenge_params['time'] -= self.challenge_params['t_decrease']

        # increasing mines number each 2 or 4 rounds
        if not self.challenge_params['score'] % self.challenge_params['d_mines']:
            self.board_params['n_mines'] += 1

        # increasing the number of rows or columns each 2 mines
        if not self.challenge_params['score'] % (self.challenge_params['d_mines'] * 4):
            self.board_params['rows'] += 1
        elif not self.challenge_params['score'] % (self.challenge_params['d_mines'] * 2):
            self.board_params['columns'] += 1

        self.challenge_params['score'] += 1
        self.board.grid(row=1)

    def new_game(self):
        """
        Load the new game. The method warp both classic and challenge methods. Call this method in the middle of a
        challenge mode game will initialize the board, without saving the progress.
        """
        try:
            self.board.destroy()
            self.detic()
        except AttributeError:
            pass
        finally:
            # after a game-over, unbind the new_game call to avoid recursive
            self.unbind('<Button-1>')
            self.board_params = self.LEVELS[self.level.get()].copy()
            self.challenge_params = self.CHALLENGE[self.level.get()].copy()
            if self.mode.get() == 'classic':
                self.classic()
            else:
                self.challenge()
            self.clock.set('Click to play')
    
    def destroy(self):
        """
        Override the Tk method destroy, so it will also save the last game setting and records.
        """
        with open('setting.json', 'w') as fp:
            json.dump(dict(mode=self.mode.get(), level=self.level.get(), theme=self.theme.get()), fp)
        self.fame.save()        # add yours filename if you want another json record file
        super(Game, self).destroy()


if __name__ == '__main__':
    Game().mainloop()
