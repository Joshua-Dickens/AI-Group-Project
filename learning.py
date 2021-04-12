import numpy as np
import random
import plot

class environment:
	def __init__(self):
		# we should use tuples for coordinates since they are immutable
		# storing tuples in a list allows us to change the pickup and dropoff locations later
		self.pickupLocations = [(4, 2), (3, 5)]
		self.dropoffLocations = [(1, 1), (1, 5), (3, 3), (5, 5)]
		self.pickupValues = [8, 8]
		self.dropoffValues = [0, 0, 0, 0]
		# Q-table maps a (state, operator) pair to a utility
		self.QTable = np.zeros([500, 6]) # TODO: add function to export this table to a .csv
		self.bot = agent()

class state:
	def __init__(self):
		self.position = [5, 1]								# agent starts in bottom left
		self.agentCarryingBlock = False						# agent starts empty-handed
		self.pickupEmpty = [False, False]					# both pickup locations start with 8 blocks
		self.dropoffFull = [False, False, False, False] 	# all dropoff locations start empty, max capacity 4 blocks

	def getOperators(self):
		# return a dictionary of {operator: utility} mappings
		index = self.hashState()
		operatorUtilities = PDWorld.QTable[index]
		operators = {}

		# add applicable operators
		if self.position[0] > 1:
			operators['north'] = operatorUtilities[0]
		if self.position[1] < 5:
			operators['east'] = operatorUtilities[1]
		if self.position[0] < 5:
			operators['south'] = operatorUtilities[2]
		if self.position[1] > 1:
			operators['west'] = operatorUtilities[3]

		if self.agentCarryingBlock == False:
			if tuple(self.position) in PDWorld.pickupLocations:
				index = PDWorld.pickupLocations.index(tuple(self.position))
				if self.pickupEmpty[index] == False:
					operators['pickup'] = operatorUtilities[4]
		else:
			if tuple(self.position) in PDWorld.dropoffLocations:
				index = PDWorld.dropoffLocations.index(tuple(self.position))
				if self.dropoffFull[index] == False:
					operators['dropoff'] = operatorUtilities[5]

		return operators

	def hashState(self):
		# return a value between 0 and 499 that can be used to index into the QTable
		index = 0
		index += 5*(self.position[0]-1) + (self.position[1]-1) # offset for position
		if self.agentCarryingBlock == False:
			index += sum([25*a*b for a,b in zip(self.pickupEmpty, [1, 2])])
		else:
			index += 100 + sum([25*a*b for a,b in zip(self.dropoffFull, [1, 2, 4, 8])])

		return index

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

		functionMapping = {'north': self.goNorth, 'east': self.goEast, 'south': self.goSouth, 'west': self.goWest, 'pickup': self.pickupBlock, 'dropoff': self.dropoffBlock}
		operator = self.policy()

		reward = functionMapping[operator]() # execute operation -- state has now changed!

		self.QLearn(operator, previousState, self.currentState, reward)

		# if final state reached, re-initialize the current state
		if (all(self.currentState.pickupEmpty) and all(self.currentState.dropoffFull)):
			PDWorld.pickupValues = [8, 8]
			PDWorld.dropoffValues = [0, 0, 0, 0]
			self.currentState = state()
			self.bankAccount = 0
			return 1

		return 0

	# Define policies
	def PRandom(self):
		# return a random operator at the current state
		operators = self.currentState.getOperators()
		if 'pickup' in operators:
			return 'pickup'
		elif 'dropoff' in operators:
			return 'dropoff'
		else:
			return random.choice(list(operators.items()))[0]
	def PGreedy(self):
		# return the operator with maximum utility at the current state
		op = self.currentState.getOperators()
		if 'pickup' in op:
			return 'pickup'
		elif 'dropoff' in op:
			return 'dropoff'
		maxValue = max(op.values())
		operators = [key for key, value in op.items() if value == maxValue]
		return random.choice(operators)
	def PExploit(self):
		# 0.2 probability of using PRandom, 0.8 probability of using PGreedy
		if random.uniform(0, 1) < 0.2:
			return self.PRandom()
		else:
			return self.PGreedy()

	def setPolicy(self, func):
		self.policy = func

	# Define operators -- note that all operators are checked in advance by getOperators()
	def goNorth(self):
		self.currentState.position[0] -= 1
		self.bankAccount -= 1
		return -1
	def goEast(self):
		self.currentState.position[1] += 1
		self.bankAccount -= 1
		return -1
	def goSouth(self):
		self.currentState.position[0] += 1
		self.bankAccount -= 1
		return -1
	def goWest(self):
		self.currentState.position[1] -= 1
		self.bankAccount -= 1
		return -1
	def pickupBlock(self):
		# determine which pickup location the agent is on
		location = PDWorld.pickupLocations.index(tuple(self.currentState.position))
		PDWorld.pickupValues[location] -= 1
		self.currentState.pickupEmpty[location] = PDWorld.pickupValues[location] == 0
		self.currentState.agentCarryingBlock = True
		self.bankAccount += 13
		return 13
	def dropoffBlock(self):
		# determine which dropoff location the agent is on
		location = PDWorld.dropoffLocations.index(tuple(self.currentState.position))
		PDWorld.dropoffValues[location] += 1
		self.currentState.dropoffFull[location] = PDWorld.dropoffValues[location] == 4
		self.currentState.agentCarryingBlock = False
		self.bankAccount += 13
		return 13

	def QLearn(self, operator, previousState, nextState, reward):
		# update QTable entry of applying operator to previousState
		# utility <- (1 - learningRate) * utility + learningRate * (reward + discountFactor * max utility over all operators in nextState)

		# get original utility of previousState
		indexDict = {'north': 0, 'east': 1, 'south': 2, 'west': 3, 'pickup': 4, 'dropoff': 5}
		operatorIndex = indexDict[operator]
		stateIndex = previousState.hashState()
		oldUtility = PDWorld.QTable[stateIndex][operatorIndex]

		# get max utility of nextState
		nextStateOperators = nextState.getOperators()
		maxUtility = max(nextStateOperators.values())
		
		# apply Q-learning to utility of operator at previousState
		newUtility = (1 - self.learningRate) * oldUtility + self.learningRate * (reward + self.discountFactor * maxUtility)
		PDWorld.QTable[stateIndex][operatorIndex] = newUtility

	def SARSALearn(self, operator, previousState, nextState, reward):
		# update QTable entry of applying operator from policy to previousState
		# utility <- (1 - learningRate ) *utility + learningRate * (reward + discountFactor * utility of operator returned by applying policy to nextState)
		
		# get original utility of previousState
		indexDict = {'north': 0, 'east': 1, 'south': 2, 'west': 3, 'pickup': 4, 'dropoff': 5}
		operatorIndex = indexDict[operator]
		stateIndex = previousState.hashState()
		oldUtility = PDWorld.QTable[stateIndex][operatorIndex]

		# get utility of applying operator returned by policy at nextState
		nextStateOperators = nextState.getOperators()
		nextOperator = self.policy()
		nextUtility = nextStateOperators[nextOperator]
		
		# apply Q-learning to utility of operator at previousState
		newUtility = (1 - self.learningRate) * oldUtility + self.learningRate * (reward + self.discountFactor * nextUtility)
		PDWorld.QTable[stateIndex][operatorIndex] = newUtility

if __name__ == "__main__":
	PDWorld = environment()
	PDWorld.bot.setPolicy(PDWorld.bot.PRandom)

	agentReward = []
	epoch = []
	epochStart = 0

	for i in range(500):
		if PDWorld.bot.step():
			epoch.append(i - epochStart)
			epochStart = i
		agentReward.append(PDWorld.bot.bankAccount)
	
	
	PDWorld.bot.setPolicy(PDWorld.bot.PExploit)
	for i in range(500, 6000):
		if PDWorld.bot.step():
			epoch.append(i - epochStart)
			epochStart = i
		agentReward.append(PDWorld.bot.bankAccount)
	
	print('number of complete deliveries: ', len(epoch))
	print('drop-off values: ', PDWorld.dropoffValues)
	print('pick-up values: ', PDWorld.pickupValues)
	print('agent holding block: ', PDWorld.bot.currentState.agentCarryingBlock)
	print('epoch: ', epoch)

	print(PDWorld.QTable[0:25])

	# plot first layer of QTable
	plot.plotQTable(PDWorld.QTable, 0)