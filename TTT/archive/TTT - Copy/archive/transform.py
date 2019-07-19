

"""
board = 0 1 2
        3 4 5
        6 7 8
"""

# def formatBoard(board):
#     newBoard = '\n'.join(["-----", ' '.join(board[0:3]), ' '.join(board[3:6]), ' '.join(board[6:9]), "-----"])
#     return newBoard


rotatePattern = [6, 3, 0,
                 7, 4, 1,
                 8, 5, 2]

flipPattern = [2, 1, 0,
               5, 4, 3,
               8, 7, 6]

def transformAux(board, pattern, n=1):
    result = board
    for _ in range(n):
        result = [result[i] for i in pattern]
    return result

def transform(board, r, f):
    rotated = transformAux(board, rotatePattern, n=r)
    rotatedAndFlipped = transformAux(rotated, flipPattern, n=f)
    return rotatedAndFlipped

def representative(board):
    sortedTransformation = sorted([(transform(board, r, f), r, f) for r in range(4) for f in range(2)])
    return sortedTransformation[0]

def restore(board, r, f):
    unflipped = transformAux(board, flipPattern, n=f)
    unrotateedAndFlipped = transformAux(unflipped, rotatePattern, n=4-r)
    return unrotateedAndFlipped

def reverseTransform(n, r, f):
    board = list('_'*9)
    board[n] = 'M'
    restoredBoard = restore(board, r, f)
    nOrig = restoredBoard.index('M')
    return nOrig

class Tests:

    def __init__(self):
        self.b1 = ['X', 'O', 'O', '.', 'X', '.', 'O', 'X', '.']
        self.b2 = ['X', '.', 'O', 'O', 'X', 'X', 'O', '.', '.']
        self.b3 = ['.', '.', 'O', 'X', 'X', 'O', 'O', '.', 'X']

    def main(self):
        print('\nRunning tests\n')

        transformations1 = sorted([(transform(self.b1, r, f), r, f) for r in range(4) for f in range(2)])
        transformations2 = sorted([(transform(self.b2, r, f), r, f) for r in range(4) for f in range(2)])
        transformations3 = sorted([(transform(self.b3, r, f), r, f) for r in range(4) for f in range(2)])

        # Print the result of transforming board b2 in all possible ways.
        # Transformation (0, 0) is the original b2.
        # Check that each board is restored to the original by restore.
        for (b, r, f) in transformations2:
            idb2 = "  <-- The original b2" if (0, 0) == (r, f) else ''
            print(f'{(r, f)}{idb2}\n{formatBoard(b)}\n')

            (rep, r, f) = representative(b)
            if b != restore(rep, r, f):
                print(formatBoard(b), formatBoard(representative(b)), formatBoard(restore(representative(b), r, f)))

        # The rest consists of tests, which produce no output if they succeed.
        if not (len(transformations1) == len(transformations2) == len(transformations3)):
            print(len(transformations1) == len(transformations2) == len(transformations3))

        for i in range(len(transformations1)):
            if not (transformations1[i][0] == transformations2[i][0] == transformations3[i][0]):
                print('=========================================')
                print((transformations1[i][1], transformations1[i][2]), '\n', formatBoard(transformations1[i][0]), sep='')
                print((transformations2[i][1], transformations2[i][2]), '\n', formatBoard(transformations2[i][0]), sep='')
                print((transformations3[i][1], transformations3[i][2]), '\n', formatBoard(transformations3[i][0]), sep='')

        for i in range(len(transformations1)):
            (board, r, f) = transformations1[i]
            if board != restore(transform(board, r, f), r, f):
                print('', (r, f), formatBoard(board), formatBoard(transform(board, r, f)), formatBoard(restore(transform(board, r, f), r, f)), sep='\n')


        print('Done')

if __name__ == '__main__':
    Tests().main()