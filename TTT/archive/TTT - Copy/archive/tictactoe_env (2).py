
# coding: utf-8

# In[15]:


import numpy as np
import random
import gym
from gym import error, spaces, utils
from gym.utils import seeding

from tkinter import *


# In[16]:


class GameManager(gym.Env):
    
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        self.action_space = spaces.Discrete(9) # always 9 possible moves, including illegal moves
        self.observation_space = spaces.Discrete(pow(3, 9)) # possible combinations is 3^9

    def step(self, action):
        
        done = False # set default to not done
        reward = -1 # set default to -1
        
        # actions are [0,1,2,3,4,5,6,7,8]
        (row_p, col_p) = (np.int8(action / 3), np.int8(action % 3)) # get row and column of move
        
        board = self.__state['board'] # get board
        player = self.__state['player'] # get player
        opponent = self.__state['opponent'] # get opponent
        mode = self.__mode # get mode for solver
        
        if board[row_p][col_p] != self.__empty_space: # illegal move
            done = True
            reward = -99
            
        else: # legal move
            
            # victory_move() returns a sequence of 'X', 'O', one for each way 
            # moving to (row_p, col_p) will win for 'X' or 'O'
            possible_win_move_p = victory_move(board, (row_p, col_p)) # check for victory
            board[row_p][col_p] = player # place piece on board
            
            if player in possible_win_move_p:  # player wins
                done = True
                reward = 100 
            
            elif not get_empty_spaces(board, self.__empty_space): # Game over; tie.
                done = True
                reward = 0   
            
            else:
                
                # Get opponent's move
                (row_o, col_o) = tictactoe_solver(board, opponent, self.__empty_space, mode)
                
                # cycle between easy and hard modes of solver
                mode = not mode 

                possible_win_move_o = victory_move(board, (row_o, col_o))
                board[row_o][col_o] = opponent
                         
                if opponent in possible_win_move_o: # opponent wins
                    done = True
                    # Return -100 if opponent wins. This is player's reward when opponent wins.
                    reward = -100 
                    
                elif not get_empty_spaces(board, self.__empty_space): # Game over; tie.
                    done = True
                    reward = 0
                    
        observation = np.copy(board)
        info = {'mode': self.__mode} # empty info   

        return (observation, reward, done, info)

    def reset(self, player = 'X', empty_space = '.'):
        self.__empty_space = empty_space
        
        self.__state = {} # initalize state dictionary
        self.__state['board'] = np.full((3,3), self.__empty_space)             
        self.__state['player'] = player
        self.__state['opponent'] = other_player(player)
        
        
        if player == 'O':    # If player is "O", have "X" make the first move
            
            (row, col) = tictactoe_solver(self.__state['board'], self.__state['opponent'], self.__empty_space)
            self.__state['board'][row][col] = self.__state['opponent']
            
        self.__mode = False
        
#        initial_observation = dict(self.__state)
        initial_observation = np.copy(self.__state['board'])
        
        return initial_observation

    
    def render(self, mode='human', close=False):
        
        tk = Tk()
        tick(self.__state['board', tk])
        tk.mainloop( )


# In[17]:


# Part of render

def tick(board, tk):
    
    for row in range(3):
        for col in range(3):
            
            button = Button(tk, text = board[row][col] , font = ('Times 16 bold'), height = 4, width = 8)
            button.grid(row = row, column = col, sticky = N + S + E + W)
    
    button.after(200, tick)


# In[18]:


def get_empty_spaces(board, empty_space):
    
    return [ (row, col) for row in range(3) for col in range(3) if board[row][col] == empty_space]             


# In[19]:


def other_player(a_player):
    return {'X': 'O', 'O': 'X'}[a_player]


# In[20]:


def tictactoe_solver(board, solver, empty_space, easy = False):
    
    """
    board: 3x3 np.array of chars: 'X', and 'O', and empty_space
    solver: 'X' or 'O'
    """
        
    opponent = other_player(solver)

    win_moves = {'X': [], 'O': []}
 
    
    possible_moves = get_empty_spaces(board, empty_space)
    
    if easy:
        return random.choice(possible_moves)

    for move in possible_moves:

        winners = victory_move(board, move)
        
        if 'X' in winners:
            win_moves['X'].append(move)

        if 'O' in winners:
            win_moves['O'].append(move)
            
    # try to win if possible
    if win_moves[solver]:
        return random.choice(win_moves[solver])

    # deny win if possible
    if win_moves[opponent]:
        return random.choice(win_moves[opponent])
    
    
    """
    possible_moves_set = set(possible_moves) 
    corner_moves_set = {(0,0), (0,2), (2,0), (2,2)}
    center_move = (1,1)
    

    # get center if its open
    if center_move in possible_moves_set:
        return center_move
    
    possible_corners = corner_moves_set & possible_moves_set
    
    # get a corner if any are open
    if possible_corners:
        return possible_corners.pop()
    """
    
    # get any possible
    return random.choice(possible_moves)


# In[21]:


def victory_move(board, possible_move):
    
    """
    possible_move is known to be blank
    to_check are triples possible 3-in-a-row 
    that include that blank.
    So if the count of X or count of O is 2
    the possible move is a winning move.
    
    Returns a list of 'X', 'O', one for each way 
    possible_move can win given current board.
    
    Don't care how many ways 'X' or 'O' can win,
    only if they can.
    """
    
    victors = []
    
    (row, col) = possible_move
    
    maj_diag = [(0,0), (1,1), (2,2)]
    min_diag = [(0,2), (1,1), (2,0)]
    
    to_check = []
    to_check.append(board[row].tolist())
    to_check.append(board[:, col].tolist())
    
    if possible_move in maj_diag:
        to_check.append(board.diagonal().tolist())
      
    if possible_move in min_diag:
        to_check.append(np.rot90(board).diagonal().tolist()) # minor diag

    for lists in to_check:
        
        if lists.count('X') is 2:
            victors.append('X')  # winner possible from this move
        if lists.count('O') is 2:
            victors.append('O') # winner possible from this move
    
    return victors

