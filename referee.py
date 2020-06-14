#!/usr/bin/env python3

"""Referee program for gobang

Note: I did not write this referee.py file. This was written by a TA from CS165A Winter 2016 ... Winter 2017
and Updated by Karl Wang for CS 165A, Spring 2020 at UC Santa Barbara

  Usage:
    referee.py board_size path_to_light_player path_to_dark_player

  Typical usage example:
    ./referee.py 11 ./gobang1 ./gobang2
"""

import string
import sys
import os
import subprocess
import threading
import signal
import re
import time
import psutil
import argparse


#TIME = 31.0      # Allowed maximum time for a movement
TIME = 100.0
TOTAL_TIME_LIMIT = 121
EMPTY = 0
DARK = 1
LIGHT = 2
CHAINLEN = 5
MOVE_REGEX = re.compile(b"[m|M]ove [p|P]layed[ \t]*:[ \t]*[a-z][0-9]{1,2}\n")

class GobangGame:
  board = None
  board_size = None

  dark_player = None
  light_player = None
  winner = EMPTY 
  moves = 0

  def __init__(self, board_size, dark_player, light_player):
    self.board_size = board_size
    self.board = [[EMPTY for x in range(0, board_size)] for x in range(0, board_size)]

    self.dark_player = dark_player
    self.light_player = light_player
    winner = EMPTY
    moves = 0

  def start_game(self):
    self.print_board()
    self.dark_player.execute(self.board_size)
    self.light_player.execute(self.board_size)

  def print_board(self):
    sys.stdout.write("  ")
    i = 0
    for c in string.ascii_lowercase:
      i += 1
      if i > self.board_size:
        break
      sys.stdout.write("   %s" % c)
    sys.stdout.write("\n   +")
    for i in range(0, self.board_size):
      sys.stdout.write("---+")
    sys.stdout.write("\n")

    for i in range(0, self.board_size):
      sys.stdout.write("%2d |" % (i + 1))
      for j in range(0, self.board_size):
        if self.board[i][j] == LIGHT:
          sys.stdout.write(" L |")
        elif self.board[i][j] == DARK:
          sys.stdout.write(" D |")
        else:
          sys.stdout.write("   |")
      sys.stdout.write("\n   +")
      for j in range(0, self.board_size):
        sys.stdout.write("---+")
      sys.stdout.write("\n")

  # Print results
  def print_results(self):
    if self.winner == DARK:
      print("Dark player wins!")
      kill_game(DARK)
    elif self.winner == LIGHT:
      print("Light player wins!")
      kill_game(LIGHT)
    else:
      print("It's a tie!")
      kill_game(0)

  def apply_move(self, row, column, color):
    score = self.update_board(row, column, color)
    self.moves += 1
    self.updateGameStatus(row, column, color)

  def is_game_over(self):
    if self.moves == self.board_size*self.board_size or self.winner != EMPTY:
      return True
    return False

  def parse_move(self, move):
    if not move:
      return None

    # Parse move
    try:
      column = ord(move[0]) - ord('a')
      row = int(move[1:]) - 1
    except ValueError:
      return None
    except TypeError:
      return None
    return row, column

  def is_valid_move(self, row, column, color):

    # Check boundaries
    if row < 0 or row > self.board_size - 1 or column < 0 or column > self.board_size - 1:
      return False

    # Tile must be empty
    if self.board[row][column] != EMPTY:
      return False

    return True

  def update_board(self, row, column, color):
    self.board[row][column] = color
    
  def updateGameStatus(self, row, col, color):
    count1 = 0
    for i in range(col, self.board_size):
      if self.board[row][i] == color:
        count1 += 1
      else:
        break
    count2 = 0
    for i in range(col, -1, -1):
      if self.board[row][i] == color:
        count2 += 1
      else:
        break
    if count1 + count2 - 1 >= CHAINLEN:
      self.winner = color
      return

    count1 = 0
    for i in range(row, self.board_size):
      if self.board[i][col] == color:
        count1 += 1
      else:
        break
    count2 = 0
    for i in range(row, -1, -1):
      if self.board[i][col] == color:
        count2 += 1
      else:
        break
    if count1 + count2 - 1 >= CHAINLEN:
      self.winner = color
      return

    count1 = 0
    i = row
    j = col
    while i >= 0 and j >= 0:
      if self.board[i][j] == color:
        count1 += 1
      else:
        break
      i -= 1
      j -= 1
    count2 = 0
    i = row
    j = col
    while i < self.board_size and j < self.board_size:
      if self.board[i][j] == color:
        count2 += 1
      else:
        break
      i += 1
      j += 1
    if count1 + count2 - 1 >= CHAINLEN:
      self.winner = color
      return

    count1 = 0
    i = row
    j = col
    while i >=0 and j < self.board_size:
      if self.board[i][j] == color:
        count1 += 1
      else:
        break
      i -= 1
      j += 1      
    count2 = 0
    i = row
    j = col
    while i < self.board_size and j >= 0:
      if self.board[i][j] == color:
        count2 += 1
      else:
        break
      i += 1
      j -= 1
    if count1 + count2 - 1 >= CHAINLEN:
      self.winner = color
    

#######################################################################

class GobangPlayer:
  score = None
  lost_turns = None
  color = None
  name = None
  executable_path = None
  executable = None
  timer = None
  stdoutput = None
  total_time = 0

  def __init__(self, color, name, executable_path):
    self.score = 2
    self.lost_turns = 0
    if color == DARK:
      self.lost_turns = -1
    self.color = color
    self.name = name
    self.executable_path = executable_path

  def kill(self):
    if self.timer:
      self.timer.cancel()
    pid = int(self.executable.pid)

    # Find process children (if any) and kill them
    try:
      for child in psutil.Process(pid).children(recursive = True):
        try:
          os.kill(child.pid, signal.SIGTERM)
        except:
          pass
    except:
      pass

    try:
      self.executable.stdin.close()
    except:
      pass
    try:
      self.executable.kill()
    except:
      pass
    try:
      self.executable.terminate()
    except:
      pass
    try:
      os.kill(pid, signal.SIGTERM)
    except:
      pass
    self.stdoutput.close()

  # Execute the program of the player
  def execute(self, board_size):
#    try:
      # Call executable
      argument_list = ["-n", str(board_size)]
      # If the program is going to be the dark player we need to pass the -l argument
      if self.color == DARK:
        argument_list.append("-l")
      self.executable = subprocess.Popen([self.executable_path] + argument_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      self.stdoutput = open(str(self.name) + ".out", "w")
#    except OSError:
#      print("Error: Could not execute %s (%s player)" % #(self.executable_path, self.name))
#      sys.exit(0)
#    except ValueError:
#      print("Error: Could not execute %s (%s player)" % #(self.executable_path, self.name))
#      sys.exit(0)

  # Start timer for player's next move
  def start_timer(self):
    # If the time limit is reached, terminate the game and have the other player win
    self.timer = threading.Timer(TIME, terminate_game, [self.color])
    self.timer.setDaemon(True)
    self.timer.start()

  # Stop timer for player's next move
  def stop_timer(self):
    self.timer.cancel()
    self.timer.join()

  # Player lost their turn
  def lost_turn(self):
    self.lost_turns += 1

  # Get and parse the player's next move
  def get_next_move(self, other_player_lost_turns):
    move = None

    # Log time to print how much time it took to get the next move
    time_begin = time.time()
    # Start timer
    self.start_timer()
    counter = 0
    # Keep reading from the pipe until the current player's move is processed
    while True:
      line = self.executable.stdout.readline()
      self.stdoutput.write(str(line.decode("utf-8")))
      self.stdoutput.flush()
      if MOVE_REGEX.match(line):
        # print("matched, other_player_lost_turns: {}, self.lost_turns {}, counter {}".format(other_player_lost_turns, self.lost_turns, counter))
        if other_player_lost_turns > 0:
          move = str(line[:-1])
          break
        counter += 1
      if counter == 2 + self.lost_turns:
        move = str(line[:-1])
        break
    # Stop timer when move is accepted
    self.stop_timer()
    time_end = time.time()
    move_time = time_end - time_begin
    self.total_time += move_time

    if self.total_time > TOTAL_TIME_LIMIT:
      print("Error: %s player reached the total time limit of 2 minutes per game" % self.name)
      print("Game over!")
      if self.color == DARK:
        print("Light player wins!")
        kill_game(LIGHT)
      else:
        print("Dark player wins!")
        kill_game(DARK)

    # Reset lost turn counter
    self.lost_turns = 0

    try:
      move_temp = move.split()[2]
      if move_temp == ":":
        move = move.split()[3][:-1]
      else:
        if sys.version_info[0] == 2:
          move = move_temp
        else:
          move = move_temp[:-1]
    except IndexError:
      print("Error: Wrong format of move: %s" % move)
      return None

    return move, move_time

  def send_next_move(self, move):
    try:
      if sys.version_info[0] == 2:
        self.executable.stdin.write("%s\n" % move)
      else:
        self.executable.stdin.write(bytes("%s\n" % move, "UTF-8"))
        self.executable.stdin.flush()
    except ValueError:
      terminate_game2(self.color)

#######################################################################

game = None

def main():
  global game

  parser = argparse.ArgumentParser(description='Gobang referee for CS 165A')
  parser.add_argument('board_size', metavar='N', type=int, help='the size of the board')
  parser.add_argument('light_executable_path', help='path to light player\'s executable')
  parser.add_argument('dark_executable_path', help='path to dark player\'s executable')

  args = parser.parse_args()

  board_size = args.board_size
  if  board_size < 5 or board_size > 26:
    print("Error: Board size must be an even integer between 4 and 26")
    sys.exit(0)

  light_executable_path = args.light_executable_path
  if not os.path.exists(light_executable_path) or not os.access(light_executable_path, os.X_OK):
    print("Error: File %s does not exist or is not executable (light player)" % light_executable_path)
    sys.exit(0)

  dark_executable_path = args.dark_executable_path
  if not os.path.exists(dark_executable_path) or not os.access(dark_executable_path, os.X_OK):
    print("Error: File %s does not exist or is not executable (dark player)" % dark_executable_path)
    sys.exit(0)

  print("Board size: %d" % board_size)
  print("Path to the executable of the light player: %s" % light_executable_path)
  print("Path to the executable of the dark player: %s" % dark_executable_path)

  dark_player = GobangPlayer(DARK, "Dark", dark_executable_path)
  light_player = GobangPlayer(LIGHT, "Light", light_executable_path)

  game = GobangGame(board_size, dark_player, light_player)
  game.start_game()

  # Start gameplay
  try:
    current_player = light_player # Set to light player so it switches to dark in the first turn
    while True:
      # Swap players in every turn
      if current_player == light_player:
        current_player = dark_player
        other_player = light_player
      else:
        current_player = light_player
        other_player = dark_player

      if True:
        print("%s player's turn" % current_player.name)
        move, move_time = current_player.get_next_move(other_player.lost_turns)

        if game.parse_move(move):
          row, column = game.parse_move(move)
        else:
          print("Error: %s player tried an invalid move (%s)" % (current_player.name, move))
          print("Game over!")
          print("%s player wins!" % other_player.name)
          kill_game(other_player.color)

        if not game.is_valid_move(row, column, current_player.color):
          print("Error: %s player tried an invalid move (%s)" % (current_player.name, move))
          print("Game over!")
          print("%s player wins!" % other_player.name)
          kill_game(other_player.color)

        print("%s player's move: %s (within %.2f seconds)" % (current_player.name, move, move_time))

        game.apply_move(row, column, current_player.color)
        game.print_board()

        if game.is_game_over():
          other_player.send_next_move(move)
          break

        # Send current player's move to the other player
        other_player.send_next_move(move)
      else:
        print("%s player has no valid moves" % current_player.name)
  except KeyboardInterrupt:
    print("Error: KeyboardInterrupt captured")
    kill_game(0)
  #except:
  #  print("Error: Unexpected exception occurred")
  #  kill_game()

  print("Game over!")
  game.print_results()


def terminate_game(color):
  print("Error: Current player takes too long to decide on their next move (%d seconds passed)" % TIME)
  print("Game over!")
  if color == DARK:
    print("Light player wins!")
    kill_game(LIGHT)
  else:
    print("Dark player wins!")
    kill_game(DARK)

def terminate_game2(color):
  print("Error: Next player is not responsive")
  print("Game over!")
  if color == DARK:
    print("Light player wins!")
    kill_game(LIGHT)
  else:
    print("Dark player wins!")
    kill_game(DARK)

def kill_game(color):
  print("Exiting...")
  game.dark_player.kill()
  game.light_player.kill()
  sys.stdout.flush()
  sys.stderr.flush()
  os._exit(color)


if __name__ == "__main__":
    main()
