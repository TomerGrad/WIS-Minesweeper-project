Instructions for our version of the game "Mine Sweeper".
***********************************************************************************************

Run via the command-line with 'root> python main.py'

***********************************************************************************************
Goal: to open all the non-mined cells on the board.

The game board is divided into cells. left-clicking on a cell would reveal one of the following: a mine would make you lose the game;
a number, indicating the number of mines diagonally and/or adjacent to it; a blank cell, which clicking on would make all
adjacent non-mined cells be automatically opened.
The first click is always a gamble, but once numbers are revealed, use them to understand which cells are potential mine locations. 
In order to avoid those cells, you can mark them with a flag (indicated as a red "¶") with a right-click- that would make them unopenable.
You can unflag a cell with another right-click.

The game has two modes: Classic mode and Challenge mode.
 In "Classic" mode , you can choose the game level (easy, normal or hard), 
which determines the number of cells the board is divided into and the number of mines (see
below). The game ends when the goal is achieved or when the user clicks a cell with a mine.
In "Challenge" mode, you can also choose the game level, but other than number of cells and
number of mines, the level determines a specific time limitation (see below). The game ends
only when you click a mine or when time is up before the goal is achieved. After every
successful round, another round starts automatically, and the clock will start ticking. As the game continues, it gets harder,
with a steeper rate as the chosen level is higher- the time assined for the round gets shorter,
and the number of mines and number of cells increase (see below).

Whenever the game is over, if you broke a record (Classic mode- shortest time to win in a certain level; Challenge mode- 
highest number of rounds played in a certain level; see different modes below), you
would be able to add you name to the "Hall of Fame".

Good Luck!
***********************************************************************************************
Levels:

Classic mode -
-----------------------------------------------
Easy: 9X9 cells, 10 mines.
Normal: 16X16 cells, 40 mines.
Hard: 30X16 cells, 99 mines.

Challenge mode - starts as in the classic mode.
-----------------------------------------------
Easy: 	starts with a 15 minutes time limitation;
	+1 mine/2 rounds (every 2 rounds, one mine is added to the board);
	-5 seconds/1 round, down to a minimum of 5 minutes;
	+1 row/4 rounds (every 4 rounds [+2mines], one row of cells is added to the board).
Normal: starts with a 10 minutes time limitation;
	+1 mine/1 round;
	-5 seconds/1 round, down to a minimum of 4 minutes;
	+1 row/2 rounds. 
Hard: 	starts with a 10 minutes time limitation;
	+1 mine/1 round;
	-6 seconds/1 round, down to a minimum of 3 minutes;
	+1 row/ 2 rounds. 
***********************************************************************************************
Orientation:

On the upper part of the board, three menus are presented: Control, Info, and Themes.
Use the Control menu to choose the mode and level of the game.
Use the Info menu to watch the "hall of fame", to reset it, or to get information about the game.
Use th Themes menu to alter the apearnace of the app. You can get extra themes by installing the ttkthemes package.

Shortcuts:
Ctrl-N:    New game. If called while challenge game is on, this will initialize it without saving the progress.
Ctrl-F:    Open the Hall of Fame
Ctrl-H:    Show this help window.
Esc:       Quit the game. Wont save the progress if a game is on.

========================================
||Made by Aviya Sharabi and Tomer Grad||
========================================