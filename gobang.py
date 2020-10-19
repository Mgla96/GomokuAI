import sys
import time
import math
import numpy as np
import random
'''
Gomoku AI
Using MiniMax with Alpha Beta Pruning 
Alpha is best value maximizer currently can guarantee at that level or above
Beta is best value that minimizer currently can guarantee at that level or above
board[row][column]
'''

def getCoordsAround(board_size, board):
    '''
    get points around placed stones
    '''
    outTpl = np.nonzero(board)  # return tuple of all non zero points on board
    potentialValsCoord = {}
    for i in range(len(outTpl[0])):
        y = outTpl[0][i]
        x = outTpl[1][i]
        if y > 0:
            potentialValsCoord[(x, y-1)] = 1
            if x > 0:
                potentialValsCoord[(x-1, y-1)] = 1
            if x < (board_size-1):
                potentialValsCoord[(x+1, y-1)] = 1
        if x > 0:
            potentialValsCoord[(x-1, y)] = 1
            if y < (board_size-1):
                potentialValsCoord[(x-1, y+1)] = 1
        if y < (board_size-1):
            potentialValsCoord[(x, y+1)] = 1
            if x < (board_size-1):
                potentialValsCoord[(x+1, y+1)] = 1
            if x > 0:
                potentialValsCoord[(x-1, y+1)] = 1
        if x < (board_size-1):
            potentialValsCoord[(x+1, y)] = 1
            if y > 0:
                potentialValsCoord[(x+1, y-1)] = 1
    finalValsX, finalValsY = [], []
    for key in potentialValsCoord:
        finalValsX.append(key[0])
        finalValsY.append(key[1])
    return finalValsX, finalValsY


def convertArrToMove(row, col):
    '''
    col goes to letter of number plus 1
    row is number but plus 1
    '''
    colVal = chr(col+ord('a'))  # 97
    rowVal = str(row+1)
    return colVal+rowVal


def convertMoveToArr(col, row):
    '''
    convert move ex: a4 to be converted to col and row integers for array
    '''
    colVal = ord(col)-ord('a')  # double check
    rowVal = int(row)-1
    return colVal, rowVal


def convertKeyToArr(key):
    '''
    convert key in getcoordsaround func to array indexes
    '''
    colVal = ord(key[0])-ord('a')  # double check
    rowVal = int(key[1:])-1
    return colVal, rowVal


def getRandomMove(board, boardSize):
    '''
    For choosing random move when can't decide propogated to center
    '''
    ctr = 0
    idx = boardSize//2
    while ctr < (idx/2):
        if board[idx+ctr][idx+ctr] == 0:
            return idx+ctr, idx+ctr
        elif board[idx+ctr][idx-ctr] == 0:
            return idx+ctr, idx-ctr
        elif board[idx+ctr][idx] == 0:
            return idx+ctr, idx
        elif board[idx][idx+ctr] == 0:
            return idx, idx+ctr
        elif board[idx][idx-ctr] == 0:
            return idx, idx-ctr
        elif board[idx-ctr][idx] == 0:
            return idx-ctr, idx
        elif board[idx-ctr][idx-ctr] == 0:
            return idx-ctr, idx-ctr
        elif board[idx-ctr][idx+ctr] == 0:
            return idx-ctr, idx+ctr
        ctr += 1
    for i in range(boardSize):
        for j in range(boardSize):
            if board[i][j] == 0:
                return i, j


def btsConvert(board, player):
    '''
    convert board to col,row,and diag string arrays for easier interpreting 
    '''
    cList, rList, dList = [], [], []
    bdiag = [board.diagonal(i) for i in range(board.shape[1]-5, -board.shape[1]+4, -1)]
    fdiag = [board[::-1, :].diagonal(i) for i in range(board.shape[1]-5, -board.shape[1]+4, -1)]
    for dgd in bdiag:
        bdiagVals = ""
        for point in dgd:
            if point == 0:
                bdiagVals += "0"
            elif point == player:
                bdiagVals += "1"
            else:
                bdiagVals += "2"
        dList.append(bdiagVals)
    for dgu in fdiag:
        fdiagVals = ""
        for point in dgu:
            if point == 0:
                fdiagVals += "0"
            elif point == player:
                fdiagVals += "1"
            else:
                fdiagVals += "2"
        dList.append(fdiagVals)
    boardT = board.copy().transpose()
    for col in boardT:
        colVals = ""
        for point in col:
            if point == 0:
                colVals += "0"
            elif point == player:
                colVals += "1"
            else:
                colVals += "2"
        cList.append(colVals)
    for row in board:
        rowVals = ""
        for point in row:
            if point == 0:
                rowVals += "0"
            elif point == player:
                rowVals += "1"
            else:
                rowVals += "2"
        rList.append(rowVals)
    return dList+cList+rList


def points(board, player):  # evaluates
    '''
    assigns points for moves
    '''
    val = 0
    player1StrArr = btsConvert(board, player)
    for i in range(len(player1StrArr)):
        len1 = len(player1StrArr[i])
        for j in range(len1):
            n = j+5
            if(n <= len1):
                st = player1StrArr[i][j:n]
                if st in patterns:
                    val += patterns[st]
        for j in range(len1):
            n = j+6
            if(n <= len1):
                st = player1StrArr[i][j:n]
                if st in patterns:
                    val += patterns[st]
    return val


def otherPlayerStone(player):
    '''
    Stones are 1 or 2 based on player. Just gets other player's stone
    '''
    return 2 if player==1 else 1

def minimax(board, isMaximizer, depth, alpha, beta, player):  # alpha, beta
    '''
    Minimax with Alpha-Beta pruning (also computer is 1st Max in this implementation)
    alpha is best already explored option along path to root for maximizer(AI)
    beta is best already explored option along path to root for minimizer(AI Opponent)
    '''
    point = points(board, player)
    if depth == 2 or point>=20000000 or point<=-20000000:
        return point
    size = len(board)
    if isMaximizer:  # THE MAXIMIZER
        best = MIN
        potentialValsX, potentialValsY = getCoordsAround(size, board)
        for i in range(len(potentialValsX)):
            if board[potentialValsY[i]][potentialValsX[i]] == 0:
                board[potentialValsY[i]][potentialValsX[i]] = player
                score = minimax(board, False, depth+1, alpha, beta, player)
                best = max(best, score)
                alpha = max(alpha, best)  # best AI Opponent move
                board[potentialValsY[i]][potentialValsX[i]] = 0  # undoing
                if beta <= alpha:
                    break
        return best
    else:  # THE MINIMIZER
        best = MAX
        potentialValsX, potentialValsY = getCoordsAround(size, board)
        for i in range(len(potentialValsX)):
            if board[potentialValsY[i]][potentialValsX[i]] == 0:
                otherplayer = otherPlayerStone(player)
                board[potentialValsY[i]][potentialValsX[i]] = otherplayer
                score = minimax(board, True, depth+1, alpha, beta, player)
                best = min(best, score)
                beta = min(beta, best)  # best AI Opponent move
                board[potentialValsY[i]][potentialValsX[i]] = 0  # undoing
                if beta <= alpha:
                    break
        return best


def computer(board_size, board, isComputerFirst):
    '''
    Chooses best move for computer
    Max that gives index and calls min in minimax 
    '''
    mostPoints = float('-inf')
    alpha,beta = MIN,MAX
    if isComputerFirst:
        mark = 1
    else:
        mark = 2
    bestMoveRow = bestMoveCol = -1
    boardSize = len(board)
    potentialValsX, potentialValsY = getCoordsAround(board_size, board)
    for i in range(len(potentialValsX)):
        if board[potentialValsY[i]][potentialValsX[i]] == 0:
            board[potentialValsY[i]][potentialValsX[i]] = mark
            movePoints = max(mostPoints, minimax(
                board, False, 1, alpha, beta, mark))
            alpha = max(alpha, movePoints)
            board[potentialValsY[i]][potentialValsX[i]] = 0
            if beta <= alpha:
                break
            if movePoints > mostPoints:
                bestMoveRow = potentialValsY[i]
                bestMoveCol = potentialValsX[i]
                mostPoints = movePoints
                if movePoints >= 20000000:
                    break
    if bestMoveRow == -1 or bestMoveCol == -1:  # ' when still -1
        bestMoveRow, bestMoveCol = getRandomMove(board, boardSize)
    board[bestMoveRow][bestMoveCol] = mark
    move = convertArrToMove(bestMoveRow, bestMoveCol)  # row,col
    return move, board


def playGame(humanFirst, board_size, board):
    '''
    basic structure of game
    '''
    playing = True
    moveNum = 0
    while playing:
        if humanFirst:  # human dark so goes first
            while True:
                val = input("move:")
                col = val[0]  # letter
                row = val[1:]  # number
                if col.isalpha() and row.isalnum():
                    colVal, rowVal = convertMoveToArr(col, row)
                    if colVal < board_size and colVal >= 0 and rowVal < board_size and rowVal >= 0 and board[rowVal][colVal] == 0:
                        board[rowVal][colVal] = 1
                        print(board)
                        break  # entered correct value
                    else:
                        print("Error invalid move: please try again")
                else:
                    print("Error invalid move: please try again")
            # then computer
            print("Move played:", val)
            moveNum += 1
            if moveNum == 1:
                moveArr = getRandomMove(board, board_size)
                move = convertArrToMove(moveArr[0], moveArr[1])
                board[moveArr[0], moveArr[1]] = 2
            else:
                move, board = computer(board_size, board, False)
            print("Move played:", move)
            print(board)
        else:  # human light so computer first
            # computer first
            if moveNum == 0:  # first move best off just placing in center of board
                idx = math.floor(board_size/2)
                if board_size % 2 == 0:
                    board[idx-1][idx-1] = 1
                    move = convertArrToMove(idx-1, idx-1)
                else:
                    board[idx][idx] = 1
                    move = convertArrToMove(idx, idx)
                moveNum += 1
            else:
                move, board = computer(board_size, board, True)
            print("Move played:", move)
            print(board)
            # then human
            while True:
                val = input("move:")
                col = val[0]  # letter
                row = val[1:]  # number
                if col.isalpha() and row.isalnum():
                    colVal, rowVal = convertMoveToArr(col, row)
                    if colVal < board_size and colVal >= 0 and rowVal < board_size and rowVal >= 0 and board[rowVal][colVal] == 0:
                        board[rowVal][colVal] = 2
                        print(board)
                        break  # entered correct value
                    else:
                        print("Error invalid move: please try again")
                else:
                    print("Error invalid move: please try again")
            print("Move played:", val)


if __name__ == "__main__":
    '''
    dark color is 1, light color is 2
    process command line arguments 
    -n size
    -l human opponent plays with light colors. If not specified, human opponent plays with dark colors
    dark player always moves first
    '''
    humanFirst = True  # human plays with dark color so human goes first
    size = 11  # if size not specified default 11*11
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "-n":
            size = sys.argv[i+1]
        if sys.argv[i] == "-l":
            humanFirst = False  # human plays with light colors so computer goes first
    board = np.zeros((int(size), int(size)))
    # for alpha beta
    MAX, MIN = math.inf, -math.inf
    patterns = {
        '11111': 30000000,
        '22222': -30000000,
        '011110': 20000000,
        '022220': -20000000,
        '011112': 50000,
        '211110': 50000,
        '022221': -50000,
        '122220': -50000,
        '01110': 30000,
        '02220': -30000,
        '011010': 15000,
        '010110': 15000,
        '022020': -15000,
        '020220': -15000,
        '001112': 2000,
        '211100': 2000,
        '002221': -2000,
        '122200': -2000,
        '211010': 2000,
        '210110': 2000,
        '010112': 2000,
        '011012': 2000,
        '122020': -2000,
        '120220': -2000,
        '020221': -2000,
        '022021': -2000,
        '01100': 500,
        '00110': 500,
        '02200': -500,
        '00220': -500
    }
    playGame(humanFirst, int(size), board)
