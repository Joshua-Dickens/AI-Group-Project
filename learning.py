import numpy as np
import random

class environment:
	def __init__(self, NUM_STATES, NUM_OPERATORS):
		# we should use tuples for coordinates since they are immutable
		# storing tuples in a list allows us to change the pickup and dropoff locations later
		self.pickupLocations = [(4, 2), (3, 5)]
		self.dropoffLocations = [(1, 1), (1, 5), (3, 3), (5, 5)]
		self.pickUpValues = [8, 8]
		self.dropOffValues = [0, 0, 0, 0]
		# Q-table maps a (state, action) pair to a utility
		self.QTable = np.zeros(500, 6)
		self.bot = agent()

class state:
	def __init__(self):
		self.position = [5, 1]              				# agent starts in bottom left
		self.agentCarryingBlock = False     				# agent starts empty-handed
		self.pickupEmpty = [False, False]					# both pickup locations start with 8 blocks
		self.dropoffFull = [False, False, False, False] 	# all dropoff locations start empty, max capacity 4 blocks

	def getOperators(self):
		# return a dictionary of {operator: utility} mappings
		index = hash(self.state)
		operatorUtilities = QTable[index]
		operators = {}

		# add applicable operators
		if self.position[0] > 1:
			operators['north'] = operatorUtilities[0]
		if self.position[1] < 5:
			operators['east'] = operatorUtilities[1]
		if self.position[0] < 1:
			operators['south'] = operatorUtilities[2]
		if self.position[1] > 1:
			operators['west'] = operatorUtilities[3]

		if self.agentCarryingBlock == False:
			if self.position in PDWorld.pickupLocations:
				index = PDWorld.pickupLocations.index(self.position)
				if pickupEmpty[index] == False:
					operators['pickup'] = operatorUtilities[4]
		else:
			if self.position in PDWorld.dropoffLocations:
				index = PDWorld.dropoffLocations.index(self.position)
				if dropoffFull[index] == True:
					operators['dropoff'] = operatorUtilities[5]

		return operators

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
		self.learningRate = 0.3
		self.discountFactor = 0.5
	
	def step(self):
		# execute policy to make one action and update q value
		# returns 1 if agent delivered all items, 0 otherwise
		previousState = self.currentState

		operationMapping = {'goNorth': self.goNorth, 'goEast': self.goEast, 'goSouth': self.goSouth, 'goWest': self.goWest, 'pickup': self.pickupBlock, 'dropoff': self.dropoffBlock}
		operator = self.policy()
		reward = operationMapping[operator] # execute operation -- state has now changed!

		QLearn(operator, previousState, self.currentState, reward)

		# if final state reached, re-initialize the current state
		if (all(self.currentState.pickupEmpty) and all(self.currentState.dropoffFull)):
			self.currentState = state()
			return 1

		return 0

	# Define policies
	def PRandom():
		# return a random operator at the current state
		operators = self.currentState.getOperators()
		item = random.choice(list(operators.items()))
		return item[0]

	def PGreedy():
		# return the operator with maximum utility at the current state
		self.currentState.getOperators()
		maxValue = max(dict.values())
		operators = [key for key, value in result.items() if value == maxValue]
		return random.choice(operators)

	def PExploit():
		# 0.2 probability of using PRandom, 0.8 probability of using PGreedy
		if random.uniform(0, 1) < 0.2:
			return PRandom()
		else:
			return PGreedy()

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

	def QLearn(self, operator, previousState, nextState, reward):
		# update QTable entry of applying operator to previousState
		# utility <- (1 - learningRate) * utility + learningRate * (reward + discountFactor * max utility over all operators in nextState)

		# get original utility of previousState
		indexDict = {'north': 0, 'east': 1, 'south': 2, 'west': 3, 'pickup': 4, 'dropoff': 5}
		operatorIndex = indexDict[operator]
		stateIndex = self.previousState.hashState()
		oldUtility = PDWorld.QTable[stateIndex][operatorIndex]

		# get max utility of nextState
		nextStateOperators = nextState.getOperators()
		maxUtility = max(nextStateOperators.values())
		
		# apply Q-learning to utility of operator at previousState
		newUtility = (1 - self.learningRate) * oldUtility + self.learningRate * (reward + self.discountFactor * maxUtility)
		PDWorld.QTable[stateIndex][operatorIndex] = newUtility

	def SARSALearn(self, operator, previousState, nextState):
		# update QTable entry of applying operator to previousState


if __name__ == "__main__":
	PDWorld = environment()
	PDWorld.bot.setPolicy(PDWorld.bot.PRandom)

	agentReward = []

	for _ in range(500):
		PDWorld.bot.step()
		agentReward += PDWorld.bot.bankAccount

	PDWorld.bot.setPolicy(PDWorld.bot.PGreedy)
	for _ in range(5500):
		PDWorld.bot.step()
		agentReward += PDWorld.bot.bankAccount