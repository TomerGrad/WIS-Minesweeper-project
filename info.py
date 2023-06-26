import time
import json

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter.simpledialog import askstring


class Fame:

    def __init__(self, root: tk.Tk, log: str = 'records.json'):
        self.root = root
        try:
            with open(log) as fp:
                self.records = json.load(fp)
        except FileNotFoundError:
            self.records = {'normal': dict(easy=None, normal=None, hard=None),
                            'challenge': dict(easy=None, normal=None, hard=None)}

    def save(self, filename='records.json') -> None:
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
        hall = tk.Toplevel(self.root)
        hall.title('Hall of Fame')
        hall.resizable(False, False)

        ttk.Label(hall,
                  text=f"The Champions of Our MineSweeper".title(),
                  anchor='center'
                  ).grid(row=0, columnspan=2, sticky=('e', 'w'))

        normal = ttk.LabelFrame(hall, text='Normal Mode', labelanchor='n', padding=4)
        for idx, (level, record) in enumerate(self.records['normal'].items()):
            name = record[0]
            score = '' if record[1] is None else time.strftime("%H:%M:%S", time.gmtime(record[1]))
            ttk.Label(normal, text=level).grid(row=idx, column=0, sticky='w', padx=4)
            ttk.Label(normal, text=name, width=24, relief='sunken').grid(row=idx, column=1)
            ttk.Label(normal, text=score, width=12, relief='sunken', anchor='center').grid(row=idx, column=2)
        normal.grid(row=1, column=0)

        challenge = ttk.LabelFrame(hall, text='Challenge Mode', labelanchor='n', padding=4)
        for idx, (level, record) in enumerate(self.records['challenge'].items()):
            name, score = record
            ttk.Label(challenge, text=level).grid(row=idx, column=0, sticky='w', padx=4)
            ttk.Label(challenge, text=name, width=24, relief='sunken').grid(row=idx, column=1)
            ttk.Label(challenge, text=score, width=12, relief='sunken', anchor='center').grid(row=idx, column=2)
        challenge.grid(row=1, column=1)

    def update(self, score: int):
        name = askstring(title='New record!', prompt='Insert the winner name:')
        self.records[self.root.mode.get()][self.root.level.get()] = (name, score)

    def reset(self):
        if msg.askokcancel('reset records', message="Are you sure?\nAll previous records will be deleted"):
            self.records = {'normal': dict(easy=('not played yet', None),
                                           normal=('not played yet', None),
                                           hard=('not played yet', None)),
                            'challenge': dict(easy=('not played yet', 0),
                                              normal=('not played yet', 0),
                                              hard=('not played yet', 0))}


def helper(root):
    try:
        with open('readme.md') as file:
            title = 'Game Help'
            body = file.read().split('___')[0]
    except FileNotFoundError:
        title = 'No help here'
        body = """Can't find the readme.md file.
Make sure you downloaded the file and placed
it in the same directory as the rest of the game's files"""

    pop = tk.Toplevel(root)
    pop.resizable(False, False)
    pop.title(title)
    ttk.Label(pop, text=body, justify='left', padding=16, anchor='center').pack(side='left')
