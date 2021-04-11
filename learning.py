import numpy as np
import random

class environment:
    def __init__(self, NUM_STATES, NUM_OPERATORS):
        # we should use tuples for coordinates since they are immutable
        # storing tuples in a list allows us to change the pickup and dropoff locations later
        self.pickupLocations = [(4, 2), (3, 5)]
        self.dropoffLocations = [(1, 1), (1, 5), (3, 3), (5, 5)]
        self.pickupValues = [8, 8]
        self.dropoffValues = [0, 0, 0, 0]
        # Q-table maps a (state, action) pair to a utility
        self.QTable = np.zeros(NUM_STATES, NUM_OPERATORS)
        self.bot = agent()

class state:
    def __init__(self):
        self.position = [5, 1]              # agent starts in bottom left
        self.agentCarryingBlock = False     # agent starts empty-handed
        self.firstPickupEmpty = False       # both pickup locations start with 8 blocks
        self.secondPickupEmpty = False
        self.firstDropoffFull = False       # all dropoff locations start empty, max capacity 4 blocks
        self.secondDropoffFull = False
        self.thirdDropoffFull = False
        self.fourthDropoffFull = False
        
    def getOperators(self):
        # return a list of valid operators in the current state
        index = hash(self.state);
        operators = QTable[index]

        # remove inapplicable operators
        if self.position[0] == 1:
            # remove north operator
        if self.position[0] == 5:
            # remove south operator
        if self.position[0] == 1:
            # remove west operator
        if self.position[1] == 5:
            # remove east operator

        # TODO: check if pickup and dropoff operators are valid
        # easiest way to do this is to get the index of the element in the pickup or dropoff list
        # if index is -1, remove the operator
        # otherwise, check if dropoffFull or pickupEmpty

    def hashState(self):
        # return a value between 0 and 499 that can be used to index into the QTable
        index = 0
        index += 5*self.position[0] + self.position[1] # offset for position (1, 1) -> (1, 2) -> (1, 3) -> ...
        if self.agentCarryingBlock ==  False:
            index += 25*(self.firstPickupEmpty + self.firstPickupEmpty*2)
        else:
            index += 25*(4 + self.firstDropoffFull + self.secondDropoffFull*2 + 
            self.thirdDropoffFull*4 + self.fourthDropoffFull*8)

class agent:
    def __init__(self):
        self.currentState = state()
        self.bankAccount = 0 # keeps track of cumulative reward
    
    def step(self):
        # execute policy to make one action
        self.policy()

    # Define policies
    def PRandom():
        # return a random operator at the current state
        self.currentState.getOperators()
        # get next state 
        nextState = self.currentState
        self.QLearn()

    def PGreedy():
        # return the operator with maximum utility at the current state
        self.currentState.getOperators()
        self.QLearn()

    def PExploit():
        # 0.2 probability of using PRandom, 0.8 probability of using PGreedy
        if random.uniform(0, 1) < 0.2:
            PRandom()
        else:
            PGreedy()

    def setPolicy(self, func):
        self.policy = func

    # Define operators -- note that all operators are checked in advance by getOperators()
    def goNorth(self):
        self.currentState.position[0] -= 1
        self.bankAccount -= 1
        return -1
    def goEast():
        self.currentState.position[1] += 1
        self.bankAccount -= 1
        return -1
    def goSouth():
        self.currentState.position[0] += 1
        self.bankAccount -= 1
        return -1
    def goWest():
        self.currentState.position[1] -= 1
        self.bankAccount -= 1
        return -1
    def pickupBlock():
        # determine which pickup location the agent is on
        self.currentState.position

        return 13
    def dropoffBlock():
        # determine which dropoff location the agent is on
        self.currentState.position

        return 13

    def QLearn(self):
        # update QTable


if __name__ == "__main__":
    PDWorld = environment(500, 6)