import time
import json

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter.simpledialog import askstring
from tkinter.scrolledtext import ScrolledText


class Fame:
    """
    Fame class is submissive to the Game class and outsourcing the management of the history records. It loading the
    proper records file if exist, update when there is a new record and save the records to json log file.
    """
    def __init__(self, root: tk.Tk, log: str = 'records.json'):
        self.root = root
        try:
            with open(log) as fp:
                self.records = json.load(fp)
        except FileNotFoundError:
            self.records = {'classic': dict(easy={}, normal={}, hard={}),
                            'challenge': dict(easy={}, normal={}, hard={})}

    def save(self, filename='records.json') -> None:
        """
        Save the records to a json file (named by default as 'records.json')
        """
        try:
            with open(filename, 'w') as fp:
                json.dump(self.records, fp, indent=4)

        except PermissionError:
            msg.showerror('Fame not yours to Claim',
                          message="""Your source file in a bad directory
Move the game files to another directory
in order to save your achievements""")

        except TypeError:
            msg.showerror('Fame not yours to Claim',
                          message="""Something gone terribly wrong
We don't sure how, but you really
messed up something with the code""")

    def show(self):
        """
        Show the Hall of Fame, allow you to show off your previous achievements, or be frustrated by over players
        """
        top = tk.Toplevel(self.root)
        top.title('Hall of Fame')
        top.resizable(False, False)
        hall = ttk.Frame(top)

        ttk.Label(hall, text=f"The Champions of Our MineSweeper".title(), anchor='center', font=dict(size=14)
                  ).grid(row=0, columnspan=2, sticky=('e', 'w'), pady=4)

        # The champions of the classic mode
        classic = ttk.LabelFrame(hall, text='Classic Mode', labelanchor='n', padding=4, width=40)
        for level in self.records['classic']:
            level_frame = ttk.LabelFrame(classic, text=level.title(), labelanchor='nw', padding=2)
            level_records = iter(sorted(self.get('classic', level).items(), key=lambda x: x[1]))
            for idx in range(5):
                try:
                    name, score = next(level_records)
                    score = time.strftime("%H:%M:%S", time.gmtime(score))
                except StopIteration:
                    name, score = 'None', ''
                ttk.Label(level_frame, text=name, width=24, relief='sunken', padding=2).grid(row=idx, column=0)
                ttk.Label(level_frame, text=score, width=12, relief='sunken', anchor='center', padding=2
                          ).grid(row=idx, column=1)
            level_frame.pack()
        classic.grid(row=1, column=0, sticky=('w', 's', 'n'))

        # The champions of the challenge mode
        challenge = ttk.LabelFrame(hall, text='Challenge Mode', labelanchor='n', padding=4)
        for level in self.records['challenge']:
            level_frame = ttk.LabelFrame(challenge, text=level.title(), labelanchor='nw', padding=2)
            level_records = iter(sorted(self.get('challenge', level).items(), key=lambda x: x[1], reverse=True))
            for idx in range(5):
                try:
                    name, score = next(level_records)
                except StopIteration:
                    name, score = 'None', ''
                ttk.Label(level_frame, text=name, width=24, relief='sunken', padding=2).grid(row=idx, column=0)
                ttk.Label(level_frame, text=score, width=12, relief='sunken', anchor='center', padding=2
                          ).grid(row=idx, column=1)
            level_frame.pack()
        challenge.grid(row=1, column=1, sticky=('e', 's', 'n'))
        hall.pack()

    def update(self, score: int, c_mode=False):
        """
        Updating the records with a new record. If there are more than 5 records per mode-level: dispose the lesser one.
        This method is blind to whenever there is a new record or to the game mode, and it's up to the Game class to
        call it properly.
        """
        mode_level_records = self.records[self.root.mode.get()].get(self.root.level.get())
        name = askstring(title='New record!', prompt='Insert the winner name:')
        while name in mode_level_records:
            name = askstring(title="Be Original", prompt="Choose other winner name:")
        if mode_level_records is not None:
            mode_level_records[name] = score

        # removing the lesser record from the records
        if len(mode_level_records) > 5:
            func = min if c_mode else max
            out = func(mode_level_records.items(), key=lambda x: x[1])[0]
            mode_level_records.pop(out)

    def get(self, mode, level) -> dict:
        """
        Return a reference of the setting game's records
        """
        return self.records[mode].get(level)

    def reset(self):
        """
        Reset the records. No going back if you chose OK.
        """
        if msg.askokcancel('reset records', message="Are you sure?\nAll previous records will be deleted"):
            self.records = {'classic': dict(easy={}, normal={}, hard={}),
                            'challenge': dict(easy={}, normal={}, hard={})}


def helper(root):
    """
    Show help window, which contains the readme-file data.
    """
    try:
        with open('README.md') as file:
            title = 'Game Help'
            body = file.read()
    except FileNotFoundError:
        title = 'No help here'
        body = """Can't find the readme file.
Make sure you downloaded it and placed
it in the same directory as the rest of the game's files"""

    pop = tk.Toplevel(root)
    pop.resizable(False, False)
    pop.title(title)
    info = ScrolledText(pop, width=96, height=32, wrap='word')
    info.insert('end', body)
    info.configure(state='disabled')

    info.pack(fill='both')

