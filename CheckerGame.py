import _thread
from BoardGUI import *
from AIPlayer import *


class CheckerGame:
    def __init__(self):
        self.opponentCheckers = None
        self.playerCheckers = None
        self.root = None
        self.lock = _thread.allocate_lock()
        self.board = self.initBoard()
        self.playerTurn = self.whoGoFirst()
        self.difficulty = self.getDifficulty()
        self.AIPlayer = AIPlayer(self, self.difficulty)
        self.GUI = BoardGUI(self)

        # AI goes first
        if not self.isPlayerTurn():
            _thread.start_new_thread(self.AIMakeMove, ())

        self.GUI.startGUI()

    # Let player decide to go first or second
    def whoGoFirst(self):
        ans = input("Do you want to go first? (Y/N) ")
        return ans == "Y" or ans == "y"

    # Let player decide level of difficulty
    def getDifficulty(self):
        ans = eval(input("What level of difficulty? (1-Easy, 2-Hard) "))
        while not (ans == 1 or ans == 2):
            print("Invalid input, please enter a value of 1 or 2")
            ans = eval(input("What level of difficulty? (1-Easy, 2-Hard) "))
        return ans

    # This function initializes the game board.
    def initBoard(self):
        board = [[0] * 8 for _ in range(8)]  # Change board size
        self.playerCheckers = set()
        self.opponentCheckers = set()
        self.checkerPositions = {}
        # Setting up checkers for an 8x8 board (3 rows each side)
        for i in range(8):
            if i < 3 or i > 4:  # Only populate 3 rows at the top and bottom
                for j in range(8):
                    if (i + j) % 2 == 1:
                        if i < 3:
                            board[i][j] = -(len(self.opponentCheckers) + 1)
                            self.opponentCheckers.add(board[i][j])
                            self.checkerPositions[board[i][j]] = (i, j)
                        else:
                            board[i][j] = len(self.playerCheckers) + 1
                            self.playerCheckers.add(board[i][j])
                            self.checkerPositions[board[i][j]] = (i, j)
        self.boardUpdated = True
        return board

    def getBoard(self):
        return self.board

    def printBoard(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                check = self.board[i][j]
                if check < 0:
                    print(check, end=' ')
                else:
                    print(' ' + str(check), end=' ')

            print()

    def isBoardUpdated(self):
        return self.boardUpdated

    def setBoardUpdated(self):
        self.lock.acquire()
        self.boardUpdated = True
        self.lock.release()

    def completeBoardUpdate(self):
        self.lock.acquire()
        self.boardUpdated = False
        self.lock.release()

    def isPlayerTurn(self):
        return self.playerTurn

    # Switch turns between player and opponent.
    # If one of them has no legal moves, the other can keep playing
    def changePlayerTurn(self):
        if self.playerTurn and self.opponentCanContinue():
            self.playerTurn = False
        elif not self.playerTurn and self.playerCanContinue():
            self.playerTurn = True

    # apply the given move in the game
    def move(self, oldrow, oldcol, row, col):
        if not self.isValidMove(oldrow, oldcol, row, col, self.playerTurn):
            return

        # human player can only choose from the possible actions
        if self.playerTurn and not ([oldrow, oldcol, row, col] in self.getPossiblePlayerActions()):
            return

        self.makeMove(oldrow, oldcol, row, col)
        _thread.start_new_thread(self.next, ())

    # update game state
    def next(self):
        if self.isGameOver():
            self.getGameSummary()
            return
        self.changePlayerTurn()
        if self.playerTurn:  # let player keep going
            return
        else:  # AI's turn
            self.AIMakeMove()

    # Temporarily Pause GUI and ask AI player to make next move.
    def AIMakeMove(self):
        self.GUI.pauseGUI()
        oldrow, oldcol, row, col = self.AIPlayer.getNextMove()
        self.move(oldrow, oldcol, row, col)
        self.GUI.resumeGUI()

    # update checker position
    def makeMove(self, oldrow, oldcol, row, col):
        toMove = self.board[oldrow][oldcol]
        self.checkerPositions[toMove] = (row, col)

        # move the checker
        self.board[row][col] = self.board[oldrow][oldcol]
        self.board[oldrow][oldcol] = 0

        # capture move, remove captured checker
        if abs(oldrow - row) == 2:
            toRemove = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
            if toRemove > 0:
                self.playerCheckers.remove(toRemove)
            else:
                self.opponentCheckers.remove(toRemove)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
            self.checkerPositions.pop(toRemove, None)

        self.setBoardUpdated()

    # Get all possible moves for the current player
    def getPossiblePlayerActions(self):
        checkers = self.playerCheckers
        regularDirs = [[-1, -1], [-1, 1]]
        captureDirs = [[-2, -2], [-2, 2]]

        regularMoves = []
        captureMoves = []
        for checker in checkers:
            oldrow = self.checkerPositions[checker][0]
            oldcol = self.checkerPositions[checker][1]
            for dir in regularDirs:
                if self.isValidMove(oldrow, oldcol, oldrow + dir[0], oldcol + dir[1], True):
                    regularMoves.append([oldrow, oldcol, oldrow + dir[0], oldcol + dir[1]])
            for dir in captureDirs:
                if self.isValidMove(oldrow, oldcol, oldrow + dir[0], oldcol + dir[1], True):
                    captureMoves.append([oldrow, oldcol, oldrow + dir[0], oldcol + dir[1]])

        # must take capture move if possible
        if captureMoves:
            return captureMoves
        else:
            return regularMoves

    # check if the given move if valid for the current player
    def isValidMove(self, oldrow, oldcol, row, col, playerTurn):
        # invalid index
        if oldrow < 0 or oldrow > 7 or oldcol < 0 or oldcol > 7 \
                or row < 0 or row > 7 or col < 0 or col > 7:
            return False
        # No checker exists in original position
        if self.board[oldrow][oldcol] == 0:
            return False
        # Another checker exists in destination position
        if self.board[row][col] != 0:
            return False

        # player's turn
        if playerTurn:
            if row - oldrow == -1:  # regular move
                return abs(col - oldcol) == 1
            elif row - oldrow == -2:  # capture move
                #  \ direction or / direction
                return (col - oldcol == -2 and self.board[row + 1][col + 1] < 0) \
                    or (col - oldcol == 2 and self.board[row + 1][col - 1] < 0)
            else:
                return False
        # opponent's turn
        else:
            if row - oldrow == 1:  # regular move
                return abs(col - oldcol) == 1
            elif row - oldrow == 2:  # capture move
                # / direction or \ direction
                return (col - oldcol == -2 and self.board[row - 1][col + 1] > 0) \
                    or (col - oldcol == 2 and self.board[row - 1][col - 1] > 0)
            else:
                return False

    # Check if the player can continue
    def playerCanContinue(self):
        directions = [[-1, -1], [-1, 1], [-2, -2], [-2, 2]]
        for checker in self.playerCheckers:
            position = self.checkerPositions[checker]
            row = position[0]
            col = position[1]
            for dir in directions:
                if self.isValidMove(row, col, row + dir[0], col + dir[1], True):
                    return True
        return False

    # Check whether opponent can continue
    def opponentCanContinue(self):
        directions = [[1, -1], [1, 1], [2, -2], [2, 2]]
        for checker in self.opponentCheckers:
            position = self.checkerPositions[checker]
            row = position[0]
            col = position[1]
            for dir in directions:
                if self.isValidMove(row, col, row + dir[0], col + dir[1], False):
                    return True
        return False

    # Neither player can can continue, thus game over
    def isGameOver(self):
        if len(self.playerCheckers) == 0 or len(self.opponentCheckers) == 0:
            return True
        else:
            return (not self.playerCanContinue()) and (not self.opponentCanContinue())

    def shutdown(self):
        # Add logic to close the GUI and any other resources
        try:
            # Attempt to close the Tkinter root window
            self.root.quit()  # This stops the mainloop
            self.root.destroy()  # This destroys the Tkinter window
        except Exception as e:
            print(f"Failed to close the GUI properly: {e}")

        try:
            pass
        except Exception as e:
            print(f"Failed to cleanly close all threads: {e}")

    def getGameSummary(self):
        self.GUI.pauseGUI()
        print("Game Over!")
        playerNum = len(self.playerCheckers)
        opponentNum = len(self.opponentCheckers)
        if (playerNum > opponentNum):
            print("Player won by {0:d} checkers! Congratulation!".format(playerNum - opponentNum))
        elif (playerNum < opponentNum):
            print("Computer won by {0:d} checkers! Try again!".format(opponentNum - playerNum))
        else:
            print("It is a draw! Try again!")
