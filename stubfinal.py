# Imports.
import numpy as np
import numpy.random as npr
import math
from SwingyMonkey import SwingyMonkey
import matplotlib.pyplot as plt
# import plotly.plotly as py



class Learner(object):
    '''
    This agent jumps randomly.
    '''

    def __init__(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity = 1
        self.last_transformed_state = None
        self.learning_parameter = 0.25
        self.discount_factor = 0.8
        self.Q = {}

    def reset(self):
        self.last_state  = None
        self.last_action = None
        self.last_reward = None
        self.gravity = 1
        self.last_transformed_state = None

    def transform(self, state):
        vertDist = math.floor((state['tree']['bot'] - state['monkey']['bot']) / 50.0)
        horDist = math.floor(state['tree']['dist'] / 75.0)
        vel = math.floor(state['monkey']['vel'] / 4.0)
        transformed_state = (vertDist, horDist, vel, self.gravity)
        return transformed_state
        
    def det_action_callback(self, state):
        
        """
        if self.last_action == 0:
            self.gravity = self.last_state['monkey']['vel'] - new_state['monkey']['vel']
        """
        #self.last_state = new_state
        self.last_action = 0
          # 0 < state['monkey']['bot'] < 60
        """
        if(tooLow):
            print "Hi"
            self.last_action = 1
        """
        tooLow = state['monkey']['bot'] < state['tree']['bot'] + 18 
        bottom = 0 < state['monkey']['bot'] < 60 #or state['tree']['dist'] < state['monkey']['bot'] 
        top = state['monkey']['bot'] > 90
        close = (59 < state['tree']['dist'] < 111) and (state['monkey']['top'] < (3 * state['tree']['bot'] / 2 + 3 * state['tree']['top'] / 2 )) 
        new_action = (bottom or close or tooLow ) and not top
        new_state = state 
        # action here should be based off of the values returned by state
        self.last_action = new_action
        self.last_state  = new_state
        """
        print new_state
        """
#        if(self.last_reward < 0):
#            self.last_action = 1
        #print state
        #print self.last_action
        return self.last_action
        
    def action_callback(self, state):
        new_state  = state
        if self.last_action >= 0:
            self.gravity = self.last_state['monkey']['vel'] - new_state['monkey']['vel']
        # tree bottom to monkey bottom, distance, monkey vel
        transformed_state = self.transform(new_state)
        new_action = 0
        if (transformed_state, True) in self.Q.keys():
            if (transformed_state, False) in self.Q.keys():
                if self.Q[transformed_state, True] > self.Q[(transformed_state, False)]:
                    new_action = True
                else:
                    new_action = False
            else:
                if self.Q[(transformed_state, 1)] > False:
                    new_action = True
                else:
                    new_action = False
        else:
            if (transformed_state, False) in self.Q.keys():
                if 0 > self.Q[(transformed_state, False)]:
                    new_action = True
                else:
                    new_action = False
            else:
                tooLow = state['monkey']['bot'] < state['tree']['bot'] + 18 
                bottom = 0 < state['monkey']['bot'] < 60 #or state['tree']['dist'] < state['monkey']['bot'] 
                top = state['monkey']['bot'] > 140
                tooHigh = state['monkey']['bot'] > state['tree']['top'] - 18 
                close = (59 < state['tree']['dist'] < 111)  and (state['monkey']['top'] < (3 * state['tree']['bot'] / 2 + 3 * state['tree']['top'] / 2 )) 
                # if((bottom or tooLow or close) and (top or tooHigh)):
                #     print state
                #     print "Oops!"
                #     if(top):
                #         print "top"
                #     if(bottom):
                #         print "bottom"
                #     if(tooLow):
                #         print "tooLow"
                #     if(tooHigh):
                #         print "tooHigh"
                new_action = (bottom or close or tooLow ) and not top and not tooHigh
                """
                new_action = npr.rand() < .1
                """                
                # 0 < state['monkey']['bot'] < 60
                """
                if (state['monkey']['bot'] - state['tree']['bot'] < 20 and state['tree']['dist'] < 60 and state['monkey']['vel'] < 0):
                    print "Hi"
                    new_action = npr.rand() < .9
                """

                """
                if (state['monkey']['bot'] - state['tree']['bot'] < 20 and state['tree']['dist'] < 100 and state['monkey']['vel'] < -5):
                    print "Hi"
                    new_action = npr.rand() < .9
                elif (state['monkey']['bot'] < 50):
                    new_action = npr.rand() < .9
                
                else:
                    new_action = npr.rand() < .1
                """

        if self.last_transformed_state:
            self.Q[(self.last_transformed_state, self.last_action)] = (1 - self.learning_parameter) * self.Q.get((self.last_transformed_state, self.last_action), 0) + self.learning_parameter * (self.last_reward + self.discount_factor * self.Q.get((transformed_state, new_action), 0))

        #print transformed_state
        self.last_action = new_action
        self.last_state  = new_state
        self.last_transformed_state = self.transform(self.last_state)

        return self.last_action

    def reward_callback(self, reward):
        '''This gets called so you can see what reward you get.'''
        self.last_reward = reward
        """
        if(reward < 0):
            print self.last_state
        """

def run_games(learner, hist, iters = 100, t_len = 100):
    '''
    Driver function to simulate learning by having the agent play a sequence of games.
    '''
    
    for ii in range(iters * 4):
        # Make a new monkey object.
        swing = SwingyMonkey(sound=False,                  # Don't play sounds.
                             text="Epoch %d" % (ii),       # Display the epoch on screen.
                             tick_length = t_len,          # Make game ticks super fast.
                             action_callback=learner.action_callback,
                             reward_callback=learner.reward_callback)

       

        # Loop until you hit something.
        while swing.game_loop():
            pass
        
        # Save score history.
        # print swing.score
        hist.append(swing.score)

        # Reset the state of the learner.
        learner.reset()

    print hist
    print learner.Q
        
    return


if __name__ == '__main__':

    # Select agent.
    agent = Learner()

    # Empty list to save history.

    fig = plt.gcf()
    hist = []

    # Run games. 
    run_games(agent, hist, 100, 10)

    # Save history. 
    np.save('hist',np.array(hist))

    plt.hist(hist)
    plt.title("Histogram")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.show()
    """
    fig = plt.gcf()
    plot_url = py.plot_mpl(fig, filename='histogram')
    """



