
from random import choice

class Player:
    """
    The board is numbered as follows.
    0 1 2
    3 4 5
    6 7 8
    """

    def __init__(self, gameManager, myMark):
        self.emptyCell = gameManager.emptyCell
        self.possibleMoves = list(range(9))  # 9 possible moves
        self.possibleWinners = gameManager.possibleWinners
        self.corners = [0, 2, 6, 8]
        self.sides = [1, 3, 5, 7]

        self.myMark = myMark
        self.opMark = self.otherMark(myMark)

        # References to GameManager functions.
        self.formatBoard = gameManager.formatBoard
        # o marksAtIndices converts a list of board indices to the marks at those indices.
        #   marksAtIndices(indices) = [board[i] for i in indices]
        self.marksAtIndices = gameManager.marksAtIndices
        # o theWinner determines if there is a winner.
        self.theWinner = gameManager.theWinner
        self.whoseTurn = gameManager.whoseTurn


    def finalReward(self, reward):
        """
        This is called after the game is over to inform the player of its final reward.
        This function should use that information in learning.
        :param reward: The final reward for the game.
        :return: None
        """
        pass

    def isAvailable(self, board, pos):
        return board[pos] == self.emptyCell

    def makeAMove(self, board, reward):
        """
        Called by the GameManager to get this player's move.
        :param board:
        :param reward:
        :return: A move
        """
        return choice(list(range(9)))

    @staticmethod
    def otherMark(mark):
        return {'X': 'O', 'O': 'X'}[mark]

    @staticmethod
    def oppositeCorner(pos):
        return {0: 8, 2: 6, 6: 2, 8: 0}[pos]

    def theWinner(self, board):
        for triple in self.possibleWinners:
            [a, b, c] = self.marksAtIndices(board, triple)
            if not self.emptyCell in [a, b, c] and a == b == c:
                return a
        return None

    def validMoves(self, board):
        valids = [i for i in range(9) if self.isAvailable(board, i)]
        return valids


class TransformableBoard:
    """
    This class represents boards that can be associated with equivalence classes of boards.
    The board is numbered as follows.
    0 1 2
    3 4 5
    6 7 8
    """

    def __init__(self):
        """
        The rotate pattern puts: the item originally in cell 6 into cell 0
                                 the item originally in cell 3 into cell 1
                                 the item originally in cell 0 into cell 2
                                 etc.
        In other words, it rotates the board 90 degrees clockwise.
        The flip pattern flips the board horizontally about its center column.
        See transformAux() to see these patterns in action.

        0 to 3 rotates and  0 or 1 flip generates all the equivalent boards.
        See representative() to see how all the equivalent boards are generated.
        """
        self.rotatePattern = [6, 3, 0,
                              7, 4, 1,
                              8, 5, 2]
        self.flipPattern = [2, 1, 0,
                            5, 4, 3,
                            8, 7, 6]

    def representative(self, board):
        """
        Generate the equivalence class of boards and select the lexicographically smallest.
        :param board:
        :return: (board, rotations, flips); rotations will be in range(4); flips will be in range(2)
                 The rotations and flips are returned so that they can be undone later.
        """
        sortedTransformation = sorted([(self.transform(board, r, f), r, f) for r in range(4) for f in range(2)])
        return sortedTransformation[0]

    def restore(self, board, r, f):
        """
        Unflip and then unrotate the board
        :param board:
        :param r:
        :param f:
        :return:
        """
        unflipped = self.transformAux(board, self.flipPattern, f)
        unrotateedAndFlipped = self.transformAux(unflipped, self.rotatePattern, 4 - r)
        return unrotateedAndFlipped

    def reverseTransformMove(self, move, r, f):
        """
        Unflip and then unrotate the move position.
        :param move:
        :param r:
        :param f:
        :return:
        """
        board = list('_' * 9)
        board[move] = 'M'
        restoredBoard = self.restore(board, r, f)
        nOrig = restoredBoard.index('M')
        return nOrig

    def transform(self, board, r, f):
        """
        Perform r rotations and then f flips on the board
        :param board:
        :param r: number of rotations
        :param f: number of flips
        :return: the rotated and flipped board
        """
        rotated = self.transformAux(board, self.rotatePattern, r)
        rotatedAndFlipped = self.transformAux(rotated, self.flipPattern, f)
        return rotatedAndFlipped

    @staticmethod
    def transformAux(board, pattern, n):
        """
        Rotate or flip the board (according to the pattern) n times.
        :param board:
        :param pattern:
        :param n:
        :return: the transformed board
        """
        result = board
        for _ in range(n):
            result = [result[i] for i in pattern]
        return result


class HumanPlayer(Player):

    def makeAMove(self, board, reward):
        print(f'\n{self.formatBoard(board)}')
        c = '-1'
        while not (c in "012345678" and (0 <= int(c) <= 8)):
            c = input(f'{self.myMark} to move > ')
        return int(c)


class LearningPlayer(Player, TransformableBoard):

    def finalReward(self, reward):
        """
        Update the qValues to include the game's final reward.
        :param reward:
        :return: None
        """
        pass

    def makeAMove(self, board, reward):
        (equivBoard, r, f) = self.representative(board)
        """
        Update qValues and select a move based on representative board from this board's equivalence class.
        Should not be random like the following.
        """
        move = choice(self.validMoves(equivBoard))
        return self.reverseTransformMove(move, r, f)


class ValidMovePlayer(Player):

    def makeAMove(self, board, reward):
        return choice(self.validMoves(board))


class PrettyGoodPlayer(ValidMovePlayer):

    def makeAMove(self, board, reward):
        """
        If this player can win, it will.
        If not, it blocks if the other player can win.
        Otherwise it makes a random valid move.
        :param board:
        :param reward:
        :return: selected move
        """
        myWins = set()
        myBlocks = set()
        emptyCell = self.emptyCell
        for possWin in self.possibleWinners:
            marks = self.marksAtIndices(board, possWin)
            if marks.count(emptyCell) == 1:
                if marks.count(self.myMark) == 2:
                    myWins.add(possWin[marks.index(emptyCell)])
                if marks.count(self.opMark) == 2:
                    myBlocks.add(possWin[marks.index(emptyCell)])
        if myWins:
            return choice(list(myWins))
        if myBlocks:
            return choice(list(myBlocks))

        emptyCellsCount = board.count(self.emptyCell)

        # X's first move should be in a corner.
        if emptyCellsCount == 9:
            return choice(self.corners)

        # O's first move should be in the center if it's available.
        if emptyCellsCount == 8 and self.isAvailable(board, 4):
            return 4

        # The following is for X's second move. It applies only if X's first move was to a corner
        xFirstMove = board.index(self.myMark)
        if emptyCellsCount == 7 and xFirstMove in self.corners:
            oFirstMove = board.index(self.opMark)
            # If O's first move is a side cell, X should take the center.
            # Otherwise, X should take the corner opposite its first move.
            if oFirstMove in self.sides:
                return 4
            if oFirstMove == 4:
                oppositeCorner = self.oppositeCorner(board.index(self.myMark))
                return oppositeCorner

        # If this is O's second move and X has diagonal corners, O should take a side move.
        availableCorners = [i for i in self.corners if self.isAvailable(board, i)]

        # If X has two adjacent corners O was forced to block (above). So, if there are 2 available corners
        # they are diagonal.
        if emptyCellsCount == 6 and len(availableCorners) == 2:
            return choice([pos for pos in self.sides if self.isAvailable(board, pos)])

        # If none of the special cases apply, take a corner if available, otherwise the center, otherwise any valid move.
        move = (choice(availableCorners) if len(availableCorners) > 0 else
                4 if self.isAvailable(board, 4) else
                super().makeAMove(board, reward)
                )
        return move


class MinimaxPlayer(PrettyGoodPlayer):

    def makeAMove(self, board, reward):
        # The first few moves are hard-wired into PrettyGoodPlayer.
        if board.count(self.emptyCell) >= 7:
            return super().makeAMove(board, reward)
        # Otherwise use minimax.
        (_, move) = self.minimax2(board)
        return move

    def makeAndEvaluateMove(self, board, move, mark):
        """
        Make the move and evaluate the board.
        :param board:
        :param move:
        :param mark:
        :return: 'X' is maximizer; 'O' is minimizer
        """
        boardCopy = board.copy()
        boardCopy[move] = mark
        val = self.evaluateBoard(boardCopy)
        return (val, move, boardCopy)

    def evaluateBoard(self, board):
        winner = self.theWinner(board)
        val = ( 1 if winner == 'X' else
               -1 if winner == 'O' else
                # winner == None. Is the game a tie because board is full?
                0 if board.count(self.emptyCell) == 0 else
                # The game is not over.
                None
                )
        if val is not None:
            print(f'\nevaluateBoard:\n{self.formatBoard(board)}\n => {val}')
        return val


    def makeMoveAndMinimax(self, board, move, mark):
        boardCopy = board.copy()
        boardCopy[move] = mark
        return self.minimax2(boardCopy, move)

    def minimax2(self, board, move=None):
        """
        Does a minimax search.
        :param board:
        :param move:
        :return: best minimax value and move for current player.
        """
        val = self.evaluateBoard(board)
        if val is not None:
            return (val, move)

        mark = self.whoseTurn(board)['mark']
        valids = self.validMoves(board)
        # minimaxResults are [(val, move)] (val in [1, 0, -1]) for move in valids]
        minimaxResults = [self.makeMoveAndMinimax(board, move, mark) for move in valids]
        minOrMax = max if mark == 'X' else min
        (bestVal, move) = minOrMax(minimaxResults, key=lambda mmMove: mmMove[0])
        print(f'\n{self.formatBoard(board)}\n{mark} => {minimaxResults} {minOrMax} {(bestVal, move)}')
        bestMoves = [(val, move) for (val, move) in minimaxResults if val == bestVal]
        return choice(bestMoves)


    def minimax(self, board):
        """
        Does a minimax search.
        :param board:
        :return: (val, move) best minimax value and move for current player.
        """
        mark = self.whoseTurn(board)['mark']
        valids = self.validMoves(board)
        # myPossMoves are [(val, move, board)] (val in [1, 0, -1, None]) for move in valids]
        # The returned boards are copies of the current board.
        myPossMoves = [self.makeAndEvaluateMove(board, move, mark) for move in valids]
        # Are any of myPossMoves winners?
        winningVal = 1 if mark == 'X' else -1
        winners = [(val, move) for (val, move, _) in myPossMoves if val == winningVal]
        if winners:
            return choice(winners)

        # There won't be any losers. A player can't lose on its own move.
        # Are there any games which are not yet decided? (val will be None.)
        stillOpen = [(move, board) for (val, move, board) in myPossMoves if val is None]
        # If stillOpen is empty, all the spaces have been taken. So game is a tie.
        if not stillOpen:
            # There is at most one tie.
            ties = [(val, move) for (val, move, _) in myPossMoves if val == 0]
            return ties[0]

        # Run minimax on the cases in which the game is not yet decided. Keep track of the move that got there.
        minimaxResults = [(self.minimax(board), move) for (move, board) in stillOpen]
        # val will be absolute: 1 for 'X' wins and -1 for 'O' wins. It is not relative to whoseMove.
        # Are we maximizing or minimizing?
        minOrMax = max if mark == 'X' else min
        # minimaxResults is a list of the form ((val, _), move).
        # The _ is the best move for the other side, which we don't care about.
        # Pick one of the moves with the best val.
        ((bestVal, _), _) = minOrMax(minimaxResults, key=lambda mmMove: mmMove[0][0])
        bestMoves = [(val, move) for ((val, _), move) in minimaxResults if val == bestVal]
        return choice(bestMoves)


