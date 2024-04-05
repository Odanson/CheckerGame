import copy    #For shallow copy of list
import math    #for mathematical function
import random   #for random moves
import datetime   # to display date and time

class AIPlayer():
    def __init__(self, game, difficulty):
        self.game = game
        self.difficulty = difficulty

    def getNextMove(self):
        if self.difficulty == 1:
            return self.getNextMoveEasy()
        elif self.difficulty == 2:
            return self.getNextMoveMedium()
        else:
            return self.getNextMoveHard()

    # Simple AI, returns a random legal move
    def getNextMoveEasy(self):
        state = AIGameState(self.game)
        moves = state.getActions(False)
        index = random.randrange(len(moves))
        chosenMove = moves[index]
        return chosenMove[0], chosenMove[1], chosenMove[2], chosenMove[3]

    # Hard AI, returns the move found by alpha-beta search with depth limit 5
    # def getNextMoveMedium(self):
    #     state = AIGameState(self.game)
    #     nextMove = self.alphaBetaSearch(state, 5)
    #     return nextMove[0], nextMove[1], nextMove[2], nextMove[3]

    # Assuming alphaBetaSearch is called like this somewhere in your class:
    def getNextMoveMedium(self):
        state = AIGameState(self.game)
        # Initialize alpha and beta for the root call
        alpha, beta = -float('inf'), float('inf')
        self.bestMove = None  # To store the best move found
        self.alphaBetaSearch(state, self.computeDepthLimit(state), alpha, beta, True)
        # After search, bestMove should hold the optimal move
        return self.bestMove if self.bestMove else (-1, -1, -1, -1)  # Fallback if no move found

    # Hard AI, returns the best move found by alpha-beta search
    # def getNextMoveHard(self):
    #     state = AIGameState(self.game)
    #     depthLimit = self.computeDepthLimit(state)
    #     nextMove = self.alphaBetaSearch(state, depthLimit)
    #     return nextMove[0], nextMove[1], nextMove[2], nextMove[3]

    def getNextMoveHard(self):
        state = AIGameState(self.game)
        depthLimit = self.computeDepthLimit(state)
        alpha = -float('inf')
        beta = float('inf')
        maximizingPlayer = True
        score, nextMove = self.alphaBetaSearch(state, depthLimit, alpha, beta, maximizingPlayer)
        if nextMove is not None:
            return nextMove  # This assumes that nextMove is a tuple like (oldrow, oldcol, row, col)
        else:
            # Handle the case where no move was found (should not occur if the game is not over)
            # You might raise an exception, return a default value, or handle it in some other way
            raise Exception("No valid move found")

    # Dynamically compute depth limit
    # Fewer checkers we have, deeper level we can search
    def computeDepthLimit(self, state):
        numcheckers = len(state.AICheckers) + len(state.humanCheckers)
        return 26 - numcheckers

    # def alphaBetaSearch(self, state, depth, alpha, beta, maximizingPlayer):
    #     if depth == 0 or state.terminalTest():
    #         return self.evaluateState(state)
    #
    #     if maximizingPlayer:
    #         value = -float('inf')
    #         for action in state.getActions(True):
    #             value = max(value, self.alphaBetaSearch(state.result(action), depth - 1, alpha, beta, False))
    #             alpha = max(alpha, value)
    #             if alpha >= beta:
    #                 break
    #         return value
    #     else:
    #         value = float('inf')
    #         for action in state.getActions(False):
    #             value = min(value, self.alphaBetaSearch(state.result(action), depth - 1, alpha, beta, True))
    #             beta = min(beta, value)
    #             if alpha >= beta:
    #                 break
    #         return value

    def alphaBetaSearch(self, state, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or state.terminalTest():
            return (self.evaluateState(state),
                    None)  # Return a tuple of score and the move (None for move because it's a terminal state)

        best_move = None  # Initialize best move

        if maximizingPlayer:
            value = -float('inf')
            for action in state.getActions(maximizingPlayer):
                new_state = state.result(action)
                score, _ = self.alphaBetaSearch(new_state, depth - 1, alpha, beta, not maximizingPlayer)
                if score > value:
                    value, best_move = score, action  # Keep track of the best score and best move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cut-off
            return (value, best_move)  # Return the score along with the best move for this branch

        else:  # Minimizing player
            value = float('inf')
            for action in state.getActions(maximizingPlayer):
                new_state = state.result(action)
                score, _ = self.alphaBetaSearch(new_state, depth - 1, alpha, beta, not maximizingPlayer)
                if score < value:
                    value, best_move = score, action  # Keep track of the best score and best move
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha cut-off
            return (value, best_move)  # Return the score along with the best move for this branch

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

            #alpha-beta min pruning
            if v <= alpha:
                self.minPruning += 1
                self.currentDepth -= 1
                return v
            beta = min(beta, v)

        self.currentDepth -= 1
        return v

    def evaluateState(self, state):
        # Simple heuristic for demonstration: difference in the number of pieces
        # More sophisticated heuristics can take into account piece positions, kings, etc.
        ai_piece_count = len(state.AICheckers)
        human_piece_count = len(state.humanCheckers)
        return ai_piece_count - human_piece_count

# a class for AI to simulate game state
class AIGameState():
    def __init__(self, game):
        # Assuming getBoard() now returns an 8x8 board
        self.board = copy.deepcopy(game.getBoard())

        self.AICheckers = set(game.opponentCheckers)
        self.humanCheckers = set(game.playerCheckers)
        self.checkerPositions = dict(game.checkerPositions)

    def humanCanContinue(self):
        directions = [[-1, -1], [-1, 1], [-2, -2], [-2, 2]]
        for checker in self.humanCheckers:
            position = self.checkerPositions[checker]
            for dir in directions:
                if self.isValidMove(position[0], position[1], position[0] + dir[0], position[1] + dir[1], True):
                    return True
        return False

    def AICanContinue(self):
        directions = [[1, -1], [1, 1], [2, -2], [2, 2]]
        for checker in self.AICheckers:
            position = self.checkerPositions[checker]
            for dir in directions:
                if self.isValidMove(position[0], position[1], position[0] + dir[0], position[1] + dir[1], False):
                    return True
        return False

    def terminalTest(self):
        if not self.AICheckers or not self.humanCheckers:
            return True
        return not (self.AICanContinue() or self.humanCanContinue())

    def isValidMove(self, oldrow, oldcol, row, col, humanTurn):
        # Updated index validation for an 8x8 board
        if oldrow < 0 or oldrow > 7 or oldcol < 0 or oldcol > 7 or row < 0 or row > 7 or col < 0 or col > 7:
            return False
        if self.board[oldrow][oldcol] == 0 or self.board[row][col] != 0:
            return False

        if humanTurn:
            if row - oldrow == -1:
                return abs(col - oldcol) == 1
            elif row - oldrow == -2:
                return (col - oldcol == -2 and self.board[row+1][col+1] < 0) or (col - oldcol == 2 and self.board[row+1][col-1] < 0)
        else:
            if row - oldrow == 1:
                return abs(col - oldcol) == 1
            elif row - oldrow == 2:
                return (col - oldcol == -2 and self.board[row-1][col+1] > 0) or (col - oldcol == 2 and self.board[row-1][col-1] > 0)
        return False

    def computeUtilityValue(self):
        utility = (len(self.AICheckers) - len(self.humanCheckers)) * 500 + len(self.AICheckers) * 50
        return utility

    def computeHeuristic(self):
        heuristic = (len(self.AICheckers) - len(self.humanCheckers)) * 50 + self.countSafeAICheckers() * 10 + len(self.AICheckers)
        return heuristic

    def countSafeAICheckers(self):
        count = 0
        for AIchecker in self.AICheckers:
            position = self.checkerPositions[AIchecker]
            safe = True
            for humanchecker in self.humanCheckers:
                humanPosition = self.checkerPositions[humanchecker]
                if abs(position[0] - humanPosition[0]) <= 2 and abs(position[1] - humanPosition[1]) <= 2:
                    safe = False
                    break
            if safe:
                count += 1
        return count

    def getActions(self, humanTurn):
        # Updated for an 8x8 board
        checkers = self.humanCheckers if humanTurn else self.AICheckers
        regularDirs = [[-1, -1], [-1, 1]] if humanTurn else [[1, -1], [1, 1]]
        captureDirs = [[-2, -2], [-2, 2]] if humanTurn else [[2, -2], [2, 2]]

        regularMoves, captureMoves = [], []
        for checker in checkers:
            position = self.checkerPositions[checker]
            for dir in regularDirs + captureDirs:
                if self.isValidMove(position[0], position[1], position[0] + dir[0], position[1] + dir[1], humanTurn):
                    move = [position[0], position[1], position[0] + dir[0], position[1] + dir[1]]
                    (captureMoves if abs(dir[0]) == 2 else regularMoves).append(move)

        return captureMoves if captureMoves else regularMoves

    def result(self, action):
        # Create a new game state as a deep copy of the current one
        new_state = copy.deepcopy(self)
        # Apply the action to the new game state
        new_state.applyAction(action)
        # Return the new game state
        return new_state

    def applyAction(self, action):
        oldrow, oldcol, row, col = action
        captured = 0

        # Move the checker
        toMove = self.board[oldrow][oldcol]
        self.checkerPositions[toMove] = (row, col)
        self.board[row][col] = toMove
        self.board[oldrow][oldcol] = 0

        # If a capture move, remove the captured checker
        if abs(oldrow - row) == 2:
            midrow, midcol = (oldrow + row) // 2, (oldcol + col) // 2
            captured = self.board[midrow][midcol]
            self.board[midrow][midcol] = 0
            self.checkerPositions.pop(captured, None)
            # Update the sets of checkers
            if captured > 0:
                self.humanCheckers.remove(captured)
            else:
                self.AICheckers.remove(-captured) # Ensure the removed ID is positive for AI checkers

        return captured

    def resetAction(self, action, captured):
        oldrow, oldcol, row, col = action

        # Move the checker back
        toMove = self.board[row][col]
        self.checkerPositions[toMove] = (oldrow, oldcol)
        self.board[oldrow][oldcol] = toMove
        self.board[row][col] = 0

        # If a capture move, restore the captured checker
        if abs(oldrow - row) == 2:
            midrow, midcol = (oldrow + row) // 2, (oldcol + col) // 2
            self.board[midrow][midcol] = captured
            self.checkerPositions[captured] = (midrow, midcol)
            # Update the sets of checkers
            if captured > 0:
                self.humanCheckers.add(captured)
            else:
                self.AICheckers.add(-captured) # Ensure the added ID is positive for AI checkers

    # def applyAction(self, action):
    #     oldrow, oldcol, row, col = action
    #     captured = 0
    #
    #     # Validate the move coordinates before proceeding
    #     if not self.isValidMove(oldrow, oldcol, row, col, self.isPlayerTurn()):
    #         return None  # Or raise an exception, or handle the error as appropriate
    #
    #     # Move the checker
    #     toMove = self.board[oldrow][oldcol]
    #     self.checkerPositions[toMove] = (row, col)
    #     self.board[row][col] = toMove
    #     self.board[oldrow][oldcol] = 0
    #
    #     # If a capture move, remove the captured checker
    #     if abs(oldrow - row) == 2:
    #         midrow, midcol = (oldrow + row) // 2, (oldcol + col) // 2
    #         captured = self.board[midrow][midcol]
    #         if captured != 0:  # Check that a checker is indeed captured
    #             self.board[midrow][midcol] = 0
    #             self.checkerPositions.pop(captured, None)
    #             # Update the sets of checkers, ensure captured checker ID is handled correctly
    #             if captured > 0:
    #                 self.humanCheckers.discard(captured)  # Use discard to avoid KeyError if item is not found
    #             elif captured < 0:
    #                 self.AICheckers.discard(-captured)  # Make sure to discard the positive ID
    #
    #     return captured
    def printBoard(self):
        for row in self.board:
            print(' '.join(f'{item:>3}' for item in row))
        print('-' * 40)  # Adjusted for an 8x8 board


    # # Apply given action to the game board.
    # # :param action: [oldrow, oldcol, newrow, newcol]
    # # :return: the label of the captured checker. 0 if none.
    # def applyAction(self, action):
    #     oldrow = action[0]
    #     oldcol = action[1]
    #     row = action[2]
    #     col = action[3]
    #     captured = 0
    #
    #     # move the checker
    #     toMove = self.board[oldrow][oldcol]
    #     self.checkerPositions[toMove] = (row, col)
    #     self.board[row][col] = toMove
    #     self.board[oldrow][oldcol] = 0
    #
    #     # capture move, remove captured checker
    #     if abs(oldrow - row) == 2:
    #         captured = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
    #         if captured > 0:
    #             self.humanCheckers.remove(captured)
    #         else:
    #             self.AICheckers.remove(captured)
    #         self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
    #         self.checkerPositions.pop(captured, None)
    #
    #     return captured
    #
    # # Reset given action to the game board. Restored captured checker if any.
    # # :param action: [oldrow, oldcol, newrow, newcol]
    # # :return: the label of the captured checker. 0 if none.
    # def resetAction(self, action, captured):
    #     oldrow = action[0]
    #     oldcol = action[1]
    #     row = action[2]
    #     col = action[3]
    #
    #     # move the checker
    #     toMove = self.board[row][col]
    #     self.checkerPositions[toMove] = (oldrow, oldcol)
    #     self.board[oldrow][oldcol] = toMove
    #     self.board[row][col] = 0
    #
    #     # capture move, remove captured checker
    #     if abs(oldrow - row) == 2:
    #         if captured > 0:
    #             self.humanCheckers.add(captured)
    #         else:
    #             self.AICheckers.add(captured)
    #         self.board[(oldrow + row) // 2][(oldcol + col) // 2] = captured
    #         self.checkerPositions[captured] = ((oldrow + row) // 2, (oldcol + col) // 2)
    #
    # def printBoard(self):
    #     for i in range(len(self.board)):
    #         for j in range(len(self.board[i])):
    #             check = self.board[i][j]
    #             if (check < 0):
    #                 print(check,end=' ')
    #             else:
    #                 print(' ' + str(check),end=' ')
    #
    #         print()
    #     print('------------------------')
