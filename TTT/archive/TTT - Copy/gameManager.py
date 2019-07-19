
# noinspection PyUnresolvedReferences
from players import HumanPlayer, LearningPlayer, MinimaxPlayer, PrettyGoodPlayer, ValidMovePlayer

class GameManager:

    def __init__(self, xPlayerClass, oPlayerClass):
        self.emptyCell =  '.'
        self.majDiag = [0, 4, 8]
        self.minDiag = [2, 4, 6]

        getRowAt = self.getRowAt
        getColAt = self.getColAt
        # These are the eight three-element sequences that could make a win.
        self.possibleWinners = [self.majDiag, self.minDiag,
                                getRowAt(0), getRowAt(3), getRowAt(6),
                                getColAt(0), getColAt(1), getColAt(2)]

        # Create the players and tell them which side they are playing.
        # The reward field is the reward to pass to the player on its next move.
        self.X = {'mark': 'X', 'reward': 0, 'player': xPlayerClass(self, 'X')}
        self.O = {'mark': 'O', 'reward': 0, 'player': oPlayerClass(self, 'O')}

    @staticmethod
    def formatBoard(board):
        boardString = '\n'.join(["-----", ' '.join(board[0:3]), ' '.join(board[3:6]), ' '.join(board[6:9]), "-----"])
        return boardString

    @staticmethod
    def getColAt(move):
        """
        Return a list of the indices for the column that includes move.
        :param move:
        :return:
        """
        colStart = move % 3
        col = [colStart, colStart+3, colStart+6]
        return col

    @staticmethod
    def getRowAt(move):
        """
        Return a list of the indices for the row that includes move.
        :param move:
        :return:
        """
        rowStart = (move//3) * 3
        row = [rowStart, rowStart+1, rowStart+2]
        return row

    def main(self):
        self.mainLoop()

    def mainLoop(self):
        board = list(self.emptyCell * 9)

        # 'X' will make the first move. We switch players at the top of the loop below.
        currentPlayer = self.O
        done = False
        winner = None
        while not done:
            currentPlayer = self.otherPlayer(currentPlayer)
            move = currentPlayer['player'].makeAMove(board.copy(), currentPlayer['reward'])
            (done, winner) = self.step(board, move)

        # Tell the players the final reward for the game.
        currentPlayer['player'].finalReward(currentPlayer['reward'])
        otherPlayer = self.otherPlayer(currentPlayer)
        otherPlayer['player'].finalReward(otherPlayer['reward'])

        result = 'Tie game.' if winner is None else f'{winner["mark"]} wins.'
        print('\n\n' + result)
        self.render(board)

    @staticmethod
    def marksAtIndices(board, indices):
        if type(indices) == str:
            print(indices)
        marks = [board[x] for x in indices]
        return marks

    def otherPlayer(self, aPlayer):
        player = {self.X['mark']: self.O, self.O['mark']: self.X}[aPlayer['mark']]
        return player

    def render(self, board):
        print(self.formatBoard(board))

    def step(self, board, move):
        """
        Make the move and return (done, winner). If no winner, winner will be None.
        :param board:
        :param move:
        :return: (done, winner)
        """
        currentPlayer = self.whoseTurn(board)
        otherPlayer = self.otherPlayer(currentPlayer)

        # The following are all game-ending cases.
        done = True
        if board[move] != self.emptyCell:
            # Illegal move. currentPlayer loses.
            currentPlayer['reward'] = -99
            otherPlayer['reward'] = 100
            print(f'\n\nInvalid move by {currentPlayer["mark"]}: {move}.', end='')
            return (done, otherPlayer)

        board[move] = currentPlayer['mark']
        if self.theWinner(board):
            # The current move won the game.
            currentPlayer['reward'] = 100
            otherPlayer['reward'] = -100
            return (done, currentPlayer)

        if board.count(self.emptyCell) == 0:
            # The game is over. It's a tie.
            currentPlayer['reward'] = 0
            otherPlayer['reward'] = 0
            return (done, None)

        # The game is not over.
        done = False
        currentPlayer['reward'] = -1
        return (done, None)

    def theWinner(self, board):
        """
        Is there a winner? If so return it. Otherwise, return None.
        """
        for triple in self.possibleWinners:
            [a, b, c] = self.marksAtIndices(board, triple)
            if a == b == c != self.emptyCell:
                return a
        return None

    def whoseTurn(self, board):
        player = self.O if board.count(self.X['mark']) > board.count(self.O['mark']) else self.X
        return player


if __name__ == '__main__':
    gameManager = GameManager(MinimaxPlayer, HumanPlayer)
    gameManager.main()


