# GomokuAI 
Created an AI to play Gomoku, otherwise known as Five in a Row. Gomoku is like tic-tac-toe except with larger game boards and the requirement of 5 of the same type of stone(a player's game piece) in a row to win. This AI uses the Minimax algorithm with Alpha-Beta Pruning and an optimized method of searching in order to determine the best move relatively quickly.<br/>

## Architecture
**getCoordsAround** - Function created to try and decrease the computation time and lower the recursive branch factor of the Minimax algorithm. It returns the coordinates of points around stones on the board which are evaluated rather than evaluating every single point on the board.<br/>
**convertArrToMove** - Takes the array indexes of the column and row and converts into the standard move format such as "a3".<br/>
**convertMoveToArr** - Takes the standard move format such as "a3" and converts it into its corresponding indexes for the game board.<br/>
**convertKeyToArr** - This is used for the getCoordsAround function which converts dictionary keys in getCoordsAround to corresponding indexes for the game board<br/>
**getRandomMove** - This Function creates a random move if my program somehow can not decide on a correct move in time<br/>
**btsConvert** - This function gets all the columns, rows, and diagonals of the numpy board array and converts it to string arrays for easier computation in the points function.<br/>
**patterns** - This is a dictionary of all move patters with assigned point weights<br/>
**points** - This function evaluates the game board based on a potential move suggested through the minimax function and returns a value of how many points this corresponds to based on patterns it sees on the game board for horizontal, vertical, diagonal down, and diagonal up orders. Each pattern has two versions, one where the player has the pattern and one where the opponent has the pattern in the patterns dictionary. If the opponent has the pattern, the weight of the pattern is negative and if the player has it, the weight is positive. This way after summing all of the weights we will get the total points for the player which is all the points for players moves minus all the points for opponents moves. For my patterns I included variations of four in a row with openings on both sides, three in a row with side blocked, three in a row with openings on both sides, four in a row but with a gap somewhere in between, three in a row but with a gap inbetween, etc...<br/>
**minimax** - Function which applies the Mini-Max algorithm with alpha beta pruning. It also uses the points function to determine how beneficial a move is and returns the beneficial point score. This is then used in the computer function where the ai will choose to place it's stone where the highest beneficial point score is.<br/>
**computer** - This function handles the computer's move. It is the first Maximizer of the minimax function. The only difference is that instead of just returning a point score like the minimax function, this returns the best mvoe as well. This function calls the minimizer in the minimax board.<br/>
**otherPlayerStone** - My board is a numpy array of 0s wtih player 1 stones represented as 1 and player 2 stones represented as 2. This function just gets the stone val of the other player.<br/>
**playGame** - This function handles the input and output requirements of the game and passes the computer function the basic requirements needed to work such as the game board, board size, and whether the human or computer moved first. <br/>

## Search
My search function uses a minimax algorithm with alpha beta pruning. The minimax algorithm begins in the computer function. Computer is the first maximizer of hte minimax algorithm but unlike my function labeled minimax, it also returns the index values of the best move, not just the points of the move. This allows us to know where the coordinates of the best move on hte board. This maximizer in the computer function calls the minimizer in the minimax function. To speed up the search time, not only do I use alpha beta pruning, but also I automatically choose moves and break from searching if they are mandatory moves to be made because not doing so would result in losing on the next move. Also, I only search for places to put stones based on places around already placed stones to speed up this search time. My point system searches through all combinations of length 5 and 6 stone/empty space patterns and checks the points from my dictionary labeled patterns. 

## How To Run

### AI VS AI

### Player VS AI
