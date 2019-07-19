

import numpy as np
import matplotlib.pyplot as plt
import tictactoe_env

# Global utilities

# Find Q[state] for a board and convert a Q[state] to a string. (Or return "not a key" if state is not a key.)    
def board_to_Qstring(board):
    state = board_to_state(board)
    if state in Q.keys(): 
        d = Q[state]
        return "Q[" + state + "]: " + str( dict( map( lambda k: (k, np.round(d[k], 1)) , d ) ) )
    else: 
        return "  " + state + " is not a key."

# A state is a string of '.', 'X', 'O'
# A board is the same sequence of characters but arranged as a 3x3 grid.
# Convert 3x3 representation to string representation.
def board_to_state(board):  
    return join(*[cell for row in board for cell in row])

env = tictactoe_env.TicTacToeEnv()

# Build printable image of 3x3 board
def format_board(board):
    rows = [join(*row, sep = "  ") for row in board]
    return join("-------", join(*rows, sep = "\n"), "-------", sep = "\n")

def game_outcome(player, final_reward): 
    return player + (" ties. " if final_reward == 0 else                      " wins. " if final_reward == 100 else " loses.")

# Get state from Q. If not defined create it as i_state (all zero's.)
# def get_Qstate(state): return Q.setdefault(state, dict(i_state)) 
def get_Qstate(board): return Q.setdefault(board_to_state(board), dict(i_state)) 

# Test games are played with the then-current Q values. No exploration.
# The last 10 games are test games. So are each test_frequency-th game and the one following.
def is_test_game(n): return n >= N-10 or n % test_frequency == 0

# The initial value of each Q[state]: {0:0, 1:0, ... , 8:0}
i_state = {}
for action in range(env.action_space.n): i_state[action] = 0
    
def is_None(arg): return type(arg) == type(None)

# Expect an arbitrary number of strings. Append them together with sep between them.
def join(*args, sep=""): return sep.join(args)

# The coefficient to use when adding an element to the moving average.
mov_avg_coeff = {'X': 50, 'O': 100}

def other_player(player): return {'X':'O', 'O':'X'}[player]

# The Q states. They are added as encountered.
Q = {}

render = False

test_frequency = 250

# Trace the final 10 games.
def trace(n): return n >= N-10


# Global run parameters

# Alpha is the learning rate. It declines with more games.
# Select the function for alpha, which is based on player, and return alpha for a given n (game number)
def alpha(n, learner): 
    alpha_fn = {'X': lambda n: min(0.5, pow(0.99, 250*n/N)), 
                'O': lambda n: min(0.75, pow(0.99, 200*n/N))}[learner] 
    return alpha_fn(n)

# Best False (traditional): 600,000 -> 96-95/43-34
# Best True  (recursive): 600,000 -> 97-95/50-46) with (MA: 50/100)
# Whether to do backprop on return from recursion.
delay_backprop = True 

# Gamma is the discount rate for future results.
def gamma(learner): return {'X': 0.9, 'O': 0.95}[learner]

# Select the player based on the game number.
# 'X' plays 1/6 of the games, 'O' plays 5/6
def learnXorO(n): 
    return 'X' if np.random.uniform() < 0.17 else 'O' 
   
# Number of games to play.    
N = 600000


#        Compute new value for Q[state][action]

#        Qs = Q[s]
#        Qnext is the state to which Qs goes after taking action a
#        max_Qnext is the current estimate of the best possible result from Qnext
#        Qsav is the current value of Q[s][a]
#        Qsav' will be the updated value of Q[s][a]

#        Transform the traditional formula to the alpha-weighted formula.
#        Qsav' += alpha * (reward + gamma * max_Qnext - Qsav)  -- Traditional formula
#        Qsav' =  Qsav + alpha * (reward + gamma * max_Qnext - Qsav)  
#        Qsav' =  Qsav + alpha * (reward + gamma * max_Qnext) - alpha * Qsav
#        Formula in terms of weights.
#        Qsav' =  (1 - alpha) * Qsav  +  alpha * (reward + gamma * max_Qnext)

def backprop(board, action, reward, next_board, done, alpha, gamma):
    
    # board will be None on the first step, which goes from None to the initial state.
    if not is_None(board):
        
        # If done, there is no next state.
        max_next_state_forecast = 0 if done                                     else max( get_Qstate( next_board ).values() )
        
        Qs = get_Qstate(board)
        
        Qs[action] = (1-alpha)*Qs[action] + alpha*(reward + gamma*max_next_state_forecast)
        


# steps is a list of tuples: (board, action, reward, next_board, done)
def finish_game(n, learner, steps):
            
    if render:
        env.render()
        print()
        
    # When called, the last step is the one just taken. So next_board is the current board.
    (_, _, _, board, _) = steps[-1]
            
    if trace(n): 
        print( format_board(board), "\n", "\n", learner, " to move:", sep = '' )
                                                         
    Qs = get_Qstate(board)
                                                                            
    # Either a random action or the action with the highest projected reward.
    action = max(Qs, key = lambda k: Qs[k]) if is_test_game(n) else env.action_space.sample()
        
    # The returned observation is the next_board.    
    (next_board, reward, done, _) = env.step(action)
    
    # Add this step to the list of steps.
    steps.append( (board, action, reward, next_board, done) ) 
        
    if trace(n): 
        print ( board_to_Qstring(board) )
        print( {"move": action, "reward": reward}, '\n' ) # win: 100; tie: 0; illegal: -99; lose: -100
        if done: 
            print(game_outcome(learner, reward))
            print(format_board(next_board))

    if done and render: env.render()
        
    # Finish the game with recursive call.    
    return (reward, steps) if done else finish_game(n, learner, steps)


def play_a_game(n, game_results, mov_avgs):
            
    learner = learnXorO(n)  
        
    if trace(n): 
        print('\nGame', n, ' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=')
        print('Learner:', learner)
        
    # The initial observation is the initial board.    
    initial_board = env.reset(player = learner, empty_space = '.')
                
    (game_reward, steps) = finish_game(n, learner, [ (None, None, None, initial_board, False) ]) 
        
    if is_test_game(n):
        mov_avgs[learner] = (mov_avgs[learner]*(mov_avg_coeff[learner] - 1) + game_reward) / mov_avg_coeff[learner]
        mov_avgs[learner + '-max'] = max(np.int(np.round(mov_avgs[learner])), mov_avgs[learner + '-max'])
        print(str(n) + '. ' + game_outcome(learner, game_reward),
              {'MA': str(mov_avgs[learner + '-max']) + ' - ' + str(int(np.round(mov_avgs[learner]))), 
               'alpha': np.round(alpha(n, learner), 2), 
               'gamma': gamma(learner)})
        game_results[learner].append( mov_avgs[learner] )
        game_results[learner + '-max'].append( mov_avgs[learner + '-max'] )
            
    for (board, action, reward, next_board, done) in (reversed(steps) if delay_backprop else steps): 
        backprop(board, action, reward, next_board, done, alpha(n, learner), gamma(learner))


def main():
        
    game_results = {'X': [],   'X-max': [],   'O': [],   'O-max': []}
    mov_avgs =     {'X': -100, 'X-max': -100, 'O': -100, 'O-max': -100}
    
    for n in range(N): play_a_game(n, game_results, mov_avgs)

    plt.plot(game_results['X'], 'b')  
    plt.plot(game_results['X-max'], 'g')  
    plt.plot(game_results['O'], 'r')  
    plt.plot(game_results['O-max'], 'g')  
    
    plt.title("Running averages - X/O (" +               str(game_results['X-max'][-1]) + '-' + str(np.int(np.round(game_results['X'][-1]))) + '/' +               str(game_results['O-max'][-1]) + '-' + str(np.int(np.round(game_results['O'][-1]))) + ')') 
    
    plt.show()


if __name__ == '__main__':
    main()



