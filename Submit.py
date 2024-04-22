import tkinter
from tkinter.font import Font
import _thread
import copy
import math
import datetime


class AIPlayer:
    def __init__(self, game, difficulty):
        self.game = game
        self.difficulty = difficulty

    #
    def getNextMove(self):
        if self.difficulty == 2:
            return self.getNextMoveEasy()
        else:
            return self.getNextMoveHard()

    # Easy AI, returns the move found by alpha-beta search with depth limit 3
    def getNextMoveEasy(self):
        state = AIGameState(self.game)
        nextMove = self.alphaBetaSearch(state, 3)
        return nextMove[0], nextMove[1], nextMove[2], nextMove[3]

    # Hard AI, returns the best move found by alpha-beta search
    def getNextMoveHard(self):
        state = AIGameState(self.game)
        depthLimit = self.computeDepthLimit(state)
        nextMove = self.alphaBetaSearch(state, depthLimit)
        return nextMove[0], nextMove[1], nextMove[2], nextMove[3]

    # Compute depth limit
    # The fewer checkers we have, the deeper the search level
    def computeDepthLimit(self, state):
        numcheckers = len(state.AICheckers) + len(state.humanCheckers)
        return 26 - numcheckers

    def alphaBetaSearch(self, state, depthLimit):
        # collect statistics for the search
        self.currentDepth = 0
        self.maxDepth = 0
        self.numNodes = 0
        self.maxPruning = 0
        self.minPruning = 0

        self.bestMove = []
        self.depthLimit = depthLimit

        starttime = datetime.datetime.now()
        v = self.maxValue(state, -1000, 1000, self.depthLimit)

        # print statistics for the search

        print("Time = " + str(datetime.datetime.now() - starttime))
        print("selected value " + str(v))
        print("(1) maximum tree depth = {0:d}".format(self.maxDepth))
        print("(2) total number of nodes generated = {0:d}".format(self.numNodes))
        print("(3) number of times pruning occurred in the MAX-VALUE() = {0:d}".format(self.maxPruning))
        print("(4) number of times pruning occurred in the MIN-VALUE() = {0:d}".format(self.minPruning))

        return self.bestMove

    # For AI player (MAX)
    def maxValue(self, state, alpha, beta, depthLimit):
        if state.terminalTest():
            return state.computeUtilityValue()
        if depthLimit == 0:
            return state.computeHeuristic()

        # update statistics for the search
        self.currentDepth += 1
        self.maxDepth = max(self.maxDepth, self.currentDepth)
        self.numNodes += 1

        v = -math.inf
        for a in state.getActions(False):
            # return captured checker if it is a capture move
            captured = state.applyAction(a)
            # state.printBoard()
            if state.humanCanContinue():
                next = self.minValue(state, alpha, beta, depthLimit - 1)
            else:  # human cannot move, AI gets one more move
                next = self.maxValue(state, alpha, beta, depthLimit - 1)
            if next > v:
                v = next
                # Keep track of the best move so far at the top level
                if depthLimit == self.depthLimit:
                    self.bestMove = a
            state.resetAction(a, captured)

            # alpha-beta max pruning
            if v >= beta:
                self.maxPruning += 1
                self.currentDepth -= 1
                return v
            alpha = max(alpha, v)

        self.currentDepth -= 1

        return v

    # For human player (MIN)
    def minValue(self, state, alpha, beta, depthLimit):
        if state.terminalTest():
            return state.computeUtilityValue()
        if depthLimit == 0:
            return state.computeHeuristic()

        # update statistics for the search
        self.currentDepth += 1
        self.maxDepth = max(self.maxDepth, self.currentDepth)
        self.numNodes += 1

        v = math.inf
        for a in state.getActions(True):
            captured = state.applyAction(a)
            if state.AICanContinue():
                next = self.maxValue(state, alpha, beta, depthLimit - 1)
            else:  # AI cannot move, human gets one more move
                next = self.minValue(state, alpha, beta, depthLimit - 1)
            if next < v:
                v = next
            state.resetAction(a, captured)

            # alpha-beta min pruning
            if v <= alpha:
                self.minPruning += 1
                self.currentDepth -= 1
                return v
            beta = min(beta, v)

        self.currentDepth -= 1
        return v


class AIGameState:
    def __init__(self, game):
        self.board = copy.deepcopy(game.getBoard())

        self.AICheckers = set(game.opponentCheckers)
        self.humanCheckers = set(game.playerCheckers)
        self.checkerPositions = dict(game.checkerPositions)

    # Check if the human player can continue.
    def humanCanContinue(self):
        directions = [[-1, -1], [-1, 1], [-2, -2], [-2, 2]]
        for checker in self.humanCheckers:
            position = self.checkerPositions[checker]
            for dir in directions:
                if self.isValidMove(position[0], position[1], position[0] + dir[0], position[1] + dir[1], True):
                    return True
        return False

    # Check if the AI player can continue.
    def AICanContinue(self):
        directions = [[1, -1], [1, 1], [2, -2], [2, 2]]
        for checker in self.AICheckers:
            position = self.checkerPositions[checker]
            row = position[0]
            col = position[1]
            for dir in directions:
                if self.isValidMove(row, col, row + dir[0], col + dir[1], False):
                    return True
        return False

    # Game over since neither player can continue
    def terminalTest(self):
        if len(self.humanCheckers) == 0 or len(self.AICheckers) == 0:
            return True
        else:
            return (not self.AICanContinue()) and (not self.humanCanContinue())

    # Check if current move is valid
    def isValidMove(self, oldrow, oldcol, row, col, humanTurn):
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

        # Human player's turn
        if humanTurn:
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

    # compute utility value of terminal state
    # utility value = difference in number of checkers * 500 + number of AI checkers * 50
    # utility value has larger weights so that is it preferred over heuristic values
    def computeUtilityValue(self):
        utility = (len(self.AICheckers) - len(self.humanCheckers)) * 500 \
                  + len(self.AICheckers) * 50
        # print("Utility value = {0:d} :: {1:d} AI vs {2:d} Human".format(utility, len(self.AICheckers),
        # len(self.humanCheckers)))
        return utility

    # compute heuristic value of a non-terminal state
    # heuristic value = diff in number of checkers * 50 + number of safe checkers * 10 + number of AI checkers
    def computeHeuristic(self):
        heurisitc = (len(self.AICheckers) - len(self.humanCheckers)) * 50 \
                    + self.countSafeAICheckers() * 10 + len(self.AICheckers)
        # print("Heuristic value = {0:d} :: {1:d} AI vs {2:d} Human".format(heurisitc, len(self.AICheckers),
        # len(self.humanCheckers)))
        return heurisitc

    # Count the number of safe AI checker.
    # A safe AI checker is one checker that no opponent can capture.
    def countSafeAICheckers(self):
        count = 0
        for AIchecker in self.AICheckers:
            AIrow = self.checkerPositions[AIchecker][0]
            AIcol = self.checkerPositions[AIchecker][1]
            safe = True
            if not (AIcol == 0 or AIcol == len(self.board[0])):
                # checkers near the boundaries are safe
                for humanchecker in self.humanCheckers:
                    if AIrow < self.checkerPositions[humanchecker][0]:
                        safe = False
                        break
            if safe:
                count += 1
        return count

    # get all possible actions for the current player
    def getActions(self, humanTurn):
        if humanTurn:
            checkers = self.humanCheckers
            regularDirs = [[-1, -1], [-1, 1]]
            captureDirs = [[-2, -2], [-2, 2]]
        else:
            checkers = self.AICheckers
            regularDirs = [[1, -1], [1, 1]]
            captureDirs = [[2, -2], [2, 2]]

        regularMoves = []
        captureMoves = []
        for checker in checkers:
            oldrow = self.checkerPositions[checker][0]
            oldcol = self.checkerPositions[checker][1]
            for dir in regularDirs:
                if self.isValidMove(oldrow, oldcol, oldrow + dir[0], oldcol + dir[1], humanTurn):
                    regularMoves.append([oldrow, oldcol, oldrow + dir[0], oldcol + dir[1]])
            for dir in captureDirs:
                if self.isValidMove(oldrow, oldcol, oldrow + dir[0], oldcol + dir[1], humanTurn):
                    captureMoves.append([oldrow, oldcol, oldrow + dir[0], oldcol + dir[1]])

        # must take capture move if possible
        if captureMoves:
            return captureMoves
        else:
            return regularMoves

    # Apply given action to the game board.
    # param action: [oldrow, oldcol, newrow, newcol]
    # return: the label of the captured checker. 0 if none.
    def applyAction(self, action):
        oldrow = action[0]
        oldcol = action[1]
        row = action[2]
        col = action[3]
        captured = 0

        # move the checker
        toMove = self.board[oldrow][oldcol]
        self.checkerPositions[toMove] = (row, col)
        self.board[row][col] = toMove
        self.board[oldrow][oldcol] = 0

        # capture move, remove captured checker
        if abs(oldrow - row) == 2:
            captured = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
            if captured > 0:
                self.humanCheckers.remove(captured)
            else:
                self.AICheckers.remove(captured)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
            self.checkerPositions.pop(captured, None)

        return captured

    # Reset given action to the game board. Restored captured checker if any.
    # param action: [oldrow, oldcol, newrow, newcol]
    # return: the label of the captured checker. 0 if none.
    def resetAction(self, action, captured):
        oldrow = action[0]
        oldcol = action[1]
        row = action[2]
        col = action[3]

        # move the checker
        toMove = self.board[row][col]
        self.checkerPositions[toMove] = (oldrow, oldcol)
        self.board[oldrow][oldcol] = toMove
        self.board[row][col] = 0

        # capture move, remove captured checker
        if abs(oldrow - row) == 2:
            if captured > 0:
                self.humanCheckers.add(captured)
            else:
                self.AICheckers.add(captured)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = captured
            self.checkerPositions[captured] = ((oldrow + row) // 2, (oldcol + col) // 2)

    def printBoard(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                check = self.board[i][j]
                if (check < 0):
                    print(check, end=' ')
                else:
                    print(' ' + str(check), end=' ')

            print()
        print('------------------------')


class BoardGUI:
    def __init__(self, game):
        self.game = game
        self.ROWS = 8
        self.COLS = 8
        self.WINDOW_WIDTH = 800  # Adjust window size if needed
        self.WINDOW_HEIGHT = 800
        self.col_width = self.WINDOW_WIDTH / self.COLS
        self.row_height = self.WINDOW_HEIGHT / self.ROWS
        self.initBoard()

    def initBoard(self):
        self.root = tkinter.Tk()
        self.c = tkinter.Canvas(self.root, width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT,
                                borderwidth=5, background='white')
        self.c.pack()
        self.board = [[0] * self.COLS for _ in range(self.ROWS)]
        self.tiles = [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]

        # Print dark square
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 1:
                    self.c.create_rectangle(i * self.row_height, j * self.col_width,
                                            (i + 1) * self.row_height, (j + 1) * self.col_width, fill="gray",
                                            outline="gray")

        # Print grid lines
        for i in range(8):
            self.c.create_line(0, self.row_height * i, self.WINDOW_WIDTH, self.row_height * i, width=2)
            self.c.create_line(self.col_width * i, 0, self.col_width * i, self.WINDOW_HEIGHT, width=2)

        # Place checks on the board
        self.updateBoard()

        # Initialize parameters
        self.checkerSelected = False
        self.clickData = {"row": 0, "col": 0, "checker": None}

        # Register callback function for mouse clicks
        self.c.bind("<Button-1>", self.processClick)

        # make GUI updates board every second
        self.root.after(1000, self.updateBoard)

        self.rules_button = tkinter.Button(self.root, text="Show Rules", command=self.show_rules)
        self.rules_button.pack(side=tkinter.BOTTOM)

        # Help button
        help_button = tkinter.Button(self.root, text="Help", command=self.show_help)
        help_button.pack(side=tkinter.BOTTOM)

    def show_rules(self):
        # Create a top-level window to display the rules
        rules_window = tkinter.Toplevel(self.root)
        rules_window.title("Game Rules")

        # Define custom fonts
        title_font = Font(family="Helvetica", size=16, weight="bold")
        text_font = Font(family="Helvetica", size=12)

        # Title Label
        title_label = tkinter.Label(rules_window, text="Game Rules", font=title_font, fg='black', bg='white')
        title_label.pack(side=tkinter.TOP, pady=10)  # padding for better spacing

        # Rules Text
        rules_text = tkinter.Text(rules_window, height=11, width=70, font=text_font, wrap=tkinter.WORD, fg='white',
                                  bg='black', padx=10, pady=10, bd=2, relief=tkinter.SUNKEN)
        rules_text.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # Define the rules text
        rules = """
    * Each player starts with 12 pieces on the three rows closest to them.
    * Pieces can only move diagonally on grey tiles.
    * Regular pieces move forward one tile; kings can move forward and backward.
    * Capture opponent pieces by jumping over them diagonally.
    * Every opportunity to capture must be taken.
    * Reach the farthest row to turn a regular piece into a king.
    * If no moves are possible for either player, the one with the most pieces wins. 
    * If both players have the same number of pieces, it's a draw."""
        rules_text.insert(tkinter.END, rules)
        rules_text.config(state=tkinter.DISABLED, bg="#27333f")

        # Add a button to close the pop-up window with styling
        close_button = tkinter.Button(rules_window, text="Close", command=rules_window.destroy, font=text_font,
                                      relief=tkinter.RAISED, bd=2)
        close_button.pack(side=tkinter.BOTTOM, pady=10)  # padding for better spacing

        # Style the window background
        rules_window.configure(background='white')

        # Center the window on the screen
        self.center_window(rules_window)

    def show_help(self):
        # Create a top-level window to display the help information
        help_window = tkinter.Toplevel(self.root)
        help_window.title("Help")

        # Define custom fonts
        text_font = Font(family="Helvetica", size=12)

        # Title Label
        title_label = tkinter.Label(help_window, text="Help", font=text_font, fg='black', bg='white')
        title_label.pack(side=tkinter.TOP, pady=10)  # padding for better spacing

        # Help Text
        help_text = tkinter.Text(help_window, height=10, width=60, font=text_font, wrap=tkinter.WORD, padx=10,
                                 fg='white', bg='black', pady=10, bd=2, relief=tkinter.SUNKEN)
        help_text.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        # Define the help text
        instructions = """How to play:
    * The human player chooses to move first or second at the start
    * Each player takes turn to make a move
    * Click on a piece to select it.
    * Click on a diagonal empty square to move the selected piece.
    * Jump over the opponent's pieces to capture them.

    For more detailed rules, refer to the 'Game Rules' section."""
        help_text.insert(tkinter.END, instructions)
        help_text.config(state=tkinter.DISABLED, bg="#27333f")  # Disable editing of the text widget

        # Add a button to close the pop-up window
        close_button = tkinter.Button(help_window, text="Close", command=help_window.destroy, font=text_font,
                                      relief=tkinter.RAISED, bd=2)
        close_button.pack(side=tkinter.TOP, pady=10)

        # Style the window background
        help_window.configure(background='white')

        # Center the help window on the screen (assuming you have a `center_window` method)
        self.center_window(help_window)

    def center_window(self, win):
        # Update "win" to calculate width and height, so geometry is set correctly
        win.update_idletasks()
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def startGUI(self):
        self.root.mainloop()

    def pauseGUI(self):
        self.c.bind("<Button-1>", '')

    def resumeGUI(self):
        self.c.bind("<Button-1>", self.processClick)

    # Update the positions of checkers
    def updateBoard(self):
        if self.game.isBoardUpdated():
            newBoard = self.game.getBoard()
            for i in range(len(self.board)):
                for j in range(len(self.board[0])):
                    if self.board[i][j] != newBoard[i][j]:
                        self.board[i][j] = newBoard[i][j]
                        self.c.delete(self.tiles[i][j])
                        self.tiles[i][j] = None

                        # choose different color for different player's checkers
                        if newBoard[i][j] < 0:
                            self.tiles[i][j] = self.c.create_oval(j * self.col_width + 10, i * self.row_height + 10,
                                                                  (j + 1) * self.col_width - 10,
                                                                  (i + 1) * self.row_height - 10,
                                                                  fill="green")
                        elif newBoard[i][j] > 0:
                            self.tiles[i][j] = self.c.create_oval(j * self.col_width + 10, i * self.row_height + 10,
                                                                  (j + 1) * self.col_width - 10,
                                                                  (i + 1) * self.row_height - 10,
                                                                  fill="red")
                        else:
                            continue

                        # raise the tiles to the highest layer
                        self.c.tag_raise(self.tiles[i][j])

            # tell game logic that GUI has updated the board
            self.game.completeBoardUpdate()

        # make GUI updates board every second
        self.root.after(1000, self.updateBoard)

    # this function checks if the checker belongs to the current player
    # if isPlayerTurn() returns True, then it is player's turn and only
    # positive checkers can be moved. Vice versa.
    def isCurrentPlayerChecker(self, row, col):
        return self.game.isPlayerTurn() == (self.board[row][col] > 0)

    # callback function that processes user's mouse clicks
    def processClick(self, event):
        col = int(event.x // self.col_width)
        row = int(event.y // self.row_height)

        # If there is no checker being selected
        if not self.checkerSelected:
            # there exists a checker at the clicked position
            # and the checker belongs to the current player
            if self.board[row][col] != 0 and self.isCurrentPlayerChecker(row, col):
                self.clickData["row"] = row
                self.clickData["col"] = col
                self.clickData["color"] = self.c.itemcget(self.tiles[row][col], 'fill')

                # replace clicked checker with a temporary checker
                self.c.delete(self.tiles[row][col])
                self.tiles[row][col] = self.c.create_oval(col * self.col_width + 10, row * self.row_height + 10,
                                                          (col + 1) * self.col_width - 10,
                                                          (row + 1) * self.row_height - 10,
                                                          fill="yellow")
                self.checkerSelected = True

            else:  # no checker at the clicked position
                return

        else:  # There is a checker being selected
            # First reset the board
            oldrow = self.clickData["row"]
            oldcol = self.clickData["col"]
            self.c.delete(self.tiles[oldrow][oldcol])
            self.tiles[oldrow][oldcol] = self.c.create_oval(oldcol * self.col_width + 10, oldrow * self.row_height + 10,
                                                            (oldcol + 1) * self.col_width - 10,
                                                            (oldrow + 1) * self.row_height - 10,
                                                            fill=self.clickData["color"])

            # If the destination leads to a legal move
            self.game.move(self.clickData["row"], self.clickData["col"], row, col)
            self.checkerSelected = False


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

    # Added
    def convert_to_king(self, piece, row):
        if (row == 0 and piece > 0) or (row == 7 and piece < 0):
            return True
        return False

    # update checker position
    # def makeMove(self, oldrow, oldcol, row, col):
    #     toMove = self.board[oldrow][oldcol]
    #     self.checkerPositions[toMove] = (row, col)
    #
    #     # move the checker
    #     self.board[row][col] = self.board[oldrow][oldcol]
    #     self.board[oldrow][oldcol] = 0
    #
    #     # capture move, remove captured checker
    #     if abs(oldrow - row) == 2:
    #         toRemove = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
    #         if toRemove > 0:
    #             self.playerCheckers.remove(toRemove)
    #         else:
    #             self.opponentCheckers.remove(toRemove)
    #         self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
    #         self.checkerPositions.pop(toRemove, None)
    #
    #     self.setBoardUpdated()

    def makeMove(self, oldrow, oldcol, row, col):
        toMove = self.board[oldrow][oldcol]
        self.checkerPositions[toMove] = (row, col)

        # Move the checker
        self.board[row][col] = toMove
        self.board[oldrow][oldcol] = 0

        # Handle capture
        if abs(oldrow - row) == 2:
            toRemove = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
            if toRemove > 0:
                self.playerCheckers.remove(toRemove)
            else:
                self.opponentCheckers.remove(toRemove)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
            self.checkerPositions.pop(toRemove, None)

        # Convert to king if necessary
        if self.convert_to_king(toMove, row):
            print(f"Piece {toMove} at ({row}, {col}) has been crowned as a king!")
            # Update the piece to indicate it's a king

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
        # Logic to close the GUI
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
        if playerNum > opponentNum:
            print("Player won by {0:d} checkers! Congratulation!".format(playerNum - opponentNum))
        elif playerNum < opponentNum:
            print("AI won by {0:d} checkers! Try again!".format(opponentNum - playerNum))
        else:
            print("It is a draw! Try again!")


if __name__ == "__main__":
    game = None
    try:
        game = CheckerGame()  # Instantiating CheckerGame starts the game and GUI
    except KeyboardInterrupt:
        print("Game was interrupted by the user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if game:
            try:
                # Assuming shutdown() is a method that properly closes the application
                game.shutdown()  # Clean up resources, close windows, etc.
            except Exception as e:
                print(f"Error during shutdown: {e}")
        print("Exiting game. Goodbye!")
