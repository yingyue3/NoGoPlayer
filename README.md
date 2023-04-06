# NoGoPlayer
University of Alberta CMPUT455 Class project

The game of NoGo is like the game of Go. It follows basically the same Rul except that catch is forbidden in NoGo game. The player who first could not make a move lose.

This player use MCTS methods to pick from simulation result.

**This project is mainly creadited to**

Name       |         email         
-- | -- 
Yingyue Cao    |     yingyue3@ualberta.ca    
Xinran Li      |     xinran1@ualberta.ca
Lingrui Zhou   |     lingrui@ualberta.ca

The team mainly contributed to file gain_weight.py, mcts.py and nogo4.py.

# Command and Run
In order to run the program, type python3 nogo4.py in the terminal.

The program mainly use GTP command to control.

Command       |         Action
-- | -- 
genmove b?w? | generate the next best move. This process is limited to 30sec
play b?w? A4 | play at the board
quit | quit the game
reset | reset the board
boardsize | adjust the board size. The default is  7x7
showboard | show the current game board
