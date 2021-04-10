import numpy as np

# create Q-table
# Q-table maps a (state, action) pair to a utility
self.NUM_STATES = 500
self.NUM_OPERATORS = 6
QTable = np.zeros([NUM_STATES, NUM_OPERATORS]) # initialize all values to 0

class environment:
    def __init__(self):
        # we should use tuples for coordinates since they are immutable
        # storing tuples in a list allows us to change the pickup and dropoff locations later
        self.pickupLocations = [(4, 2), (3, 5)]
        self.dropoffLocations = [(1, 1), (1, 5), (3, 3), (5, 5)]
        self.bot = agent()

class state:
    def __init__(self):
        self.position = [5, 1]          # agent starts in bottom left
        self.agentCarryingBlock = False    # agent starts empty-handed
        self.firstPickupEmpty = False   # both pickup locations start with 8 blocks
        self.secondPickupEmpty = False
        self.firstDropoffFull = False   # all dropoff locations start empty, max capacity 4 blocks
        self.secondDropoffFull = False
        self.thirdDropoffFull = False
        self.fourthDropoffFull = False

    def getMaxUtility(self):
        # index into QTable and return operator with maximum utility
        index = hashState()
        return np.argmax(QTable[index])

    def hashState(self):
        # return a value between 0 and 499 that can be used to index into the QTable
        index = 0
        index += 5*self.position[0] + self.position[1] # offset for position (1, 1) -> (1, 2) -> (1, 3) -> ...
        if self.agentCarryingBlock == False:
            index += 25*(self.firstPickupEmpty + self.firstPickupEmpty*2) # offset for 
        else:
            index += 25*(self.firstDropoffFull + self.secondDropoffFull*2 + 
            self.thirdDropoffFull*4 + self.fourthDropoffFull*8)
            index += 100 # first 100 indices are reserved for if agent is not carrying a block

class agent:
    def __init__(self):
        self.currentState = state()
        self.policy =

    