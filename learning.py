import numpy as np
import random
from plot import plotQTable, plotLineGraph
from copy import deepcopy
import os

class environment:
	def __init__(self, debug = False):
		# we should use tuples for coordinates since they are immutable
		# storing tuples in a list allows us to change the pickup and dropoff locations later
		self.pickupLocations = [(4, 2), (3, 5)]
		self.dropoffLocations = [(1, 1), (1, 5), (3, 3), (5, 5)]
		self.pickupValues = [8, 8]
		self.dropoffValues = [0, 0, 0, 0]
		# Q-table maps a (state, operator) pair to a utility
		self.QTable = np.zeros([500, 6])		
		self.bot = agent()
		self.debug = debug

	def setEdges(self):
		# set invalid QTable values to min value of table
		for i in range(20):
			topLeftIndex = i*25
			maxFrameValue = np.max(self.QTable[topLeftIndex:topLeftIndex+24])
			minFrameValue = np.min(self.QTable[topLeftIndex:topLeftIndex+24])
			r = (maxFrameValue - minFrameValue)
			value = minFrameValue - 0.1 * r
			for j in range(5):
				self.QTable[topLeftIndex+j][0] = value # north
			for j in range(5):
				self.QTable[topLeftIndex+20+j][2] = value # south
			for j in range(5):
				self.QTable[topLeftIndex+(j*5+4)][1] = value # east
			for j in range(5):
				self.QTable[topLeftIndex + j*5][3] = value # west

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

	# setter functions
	def setLearningRate(self, lr):
		self.learningRate = lr
	def setDiscountFactor(self, df):
		self.discountFactor = df
	def setPolicy(self, func):
		self.policy = func
	def setLearn(self, learn):
		self.learning = learn
	
	# getter functions
	def getPolicy(self):
		if self.policy == self.PRandom:
			return 'PRandom'
		elif self.policy == self.PGreedy:
			return 'PGreedy'
		else:
			return 'PExploit'
	
	def step(self):
		# execute policy to make one action and update q value
		# returns 1 if agent delivered all items, 0 otherwise
		if PDWorld.debug == True:
			print('Step function')
			print(f'Agent account is {self.bankAccount}')
			print('Agent is in position ', self.currentState.position)
			print(f'Pickup location availabilies are {[not i for i in self.currentState.pickupEmpty]}')
			print(f'Dropoff location availabilies are {[not i for i in self.currentState.dropoffFull]}')
			print(f'QTable index is {self.currentState.hashState()}')
			input('Press enter to continue')

		# save previous state info
		previousState = deepcopy(self.currentState)

		functionMapping = {'north': self.goNorth, 'east': self.goEast, 'south': self.goSouth, 'west': self.goWest, 'pickup': self.pickupBlock, 'dropoff': self.dropoffBlock}
		operator = self.policy()
		if PDWorld.debug == True:
			print(f'Agent will execute {operator}')
			input('Press enter to continue')

		reward = functionMapping[operator]() # execute operation -- state has now changed!
		if PDWorld.debug == True:
			print('Step function')
			print(f'Agent account is now {self.bankAccount}')
			print('Agent is now in position ', self.currentState.position)
			print(f'New pickup location availabilies are {[not i for i in self.currentState.pickupEmpty]}')
			print(f'New dropoff location availabilies are {[not i for i in self.currentState.dropoffFull]}')
			print(f'New QTable index is {self.currentState.hashState()}')
			input('Press enter to continue')

		self.QLearn(operator, previousState, self.currentState, reward)

		# TODO: plot QTable if first dropoff location reached

		# if final state reached, re-initialize the current state
		if (all(self.currentState.pickupEmpty) and all(self.currentState.dropoffFull)):
			if PDWorld.debug == True:
				print('Agent has delivered final package -- resetting world')
				print('Press enter to continue')
			PDWorld.pickupValues = [8, 8]
			PDWorld.dropoffValues = [0, 0, 0, 0]
			self.currentState = state()
			return 1

		return 0

	# Define policies
	def PRandom(self):
		# return a random operator at the current state
		operators = self.currentState.getOperators()
		if PDWorld.debug == True:
			print('Agent policy is PRandom')
			print('Agent action(s) is/are ', operators)
		
		if 'pickup' in operators:
			return 'pickup'
		elif 'dropoff' in operators:
			return 'dropoff'
		else:
			return random.choice(list(operators.items()))[0]
	def PGreedy(self):
		# return the operator with maximum utility at the current state
		op = self.currentState.getOperators()
		if PDWorld.debug == True:
			print('Agent policy is PGreedy')
			print('Agent action(s) is/are ', op)
		if 'pickup' in op:
			return 'pickup'
		elif 'dropoff' in op:
			return 'dropoff'
		maxValue = max(op.values())
		operators = [key for key, value in op.items() if value == maxValue]
		return random.choice(operators)
	def PExploit(self):
		if PDWorld.debug == True:
			print('Agent policy is PExploit')
		# 0.2 probability of using PRandom, 0.8 probability of using PGreedy
		if random.uniform(0, 1) < 0.2:
			return self.PRandom()
		else:
			return self.PGreedy()

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
		# check if agent filled first dropoff location
		if sum(self.currentState.dropoffFull) == 1 and not os.path.exists('img/firstdropoff'):
			# only one dropoff location is full
				os.makedirs('img/firstdropoff')
				for i in range(20):
					plotQTable(PDWorld.QTable, i, False, True, 'img/firstdropoff/')

		self.currentState.agentCarryingBlock = False
		self.bankAccount += 13
		return 13

	# Q-Learning function
	def QLearn(self, operator, previousState, nextState, reward):
		# update QTable entry of applying operator to previousState
		# utility <- (1 - learningRate) * utility + learningRate * (reward + discountFactor * max utility over all operators in nextState)
		
		if PDWorld.debug == True:
			print(f'Updating utility of operator {operator} in state {previousState.hashState()} with reward {reward} and terminal state {nextState.hashState()}')
			input('Press enter to continue')

		# get original utility of previousState
		previousStateOperators = previousState.getOperators()
		oldUtility = previousStateOperators[operator]
		if PDWorld.debug == True:
			print(f'Utilities of operators at state {previousState.hashState()} are {previousStateOperators}')
			print(f'Utility of {operator} is {oldUtility}')
			input('Press enter to continue')

		if self.learning == 'QLearn':
			# get max utility of nextState
			nextStateOperators = nextState.getOperators()
			maxUtility = max(nextStateOperators.values())
			if PDWorld.debug == True:
				print(f'Utilities of operators at state {nextState.hashState()} are {nextStateOperators}')
				print(f'Max utility is {maxUtility}')
				input('Press enter to continue')
			# apply Q-learning to utility of operator at previousState
			newUtility = (1 - self.learningRate) * oldUtility + self.learningRate * (reward + self.discountFactor * maxUtility)
		elif self.learning == 'SARSALearn':
			# get utility of applying operator returned by policy at nextState
			nextStateOperators = nextState.getOperators()
			nextOperator = self.policy()
			nextUtility = nextStateOperators[nextOperator]
			# Apply SARSA-learning to utility of operator at previousState
			newUtility = (1 - self.learningRate) * oldUtility + self.learningRate * (reward + self.discountFactor * nextUtility)

		# update QTable
		indexDict = {'north': 0, 'east': 1, 'south': 2, 'west': 3, 'pickup': 4, 'dropoff': 5}
		operatorIndex = indexDict[operator]
		stateIndex = previousState.hashState()
		PDWorld.QTable[stateIndex][operatorIndex] = newUtility
		if PDWorld.debug == True:
			print(f'Utility of operator {operator} at state {stateIndex} is now {newUtility}')
			input('Press enter to start next step')

if __name__ == "__main__":
	PDWorld = environment(debug=False)
	PDWorld.bot.setPolicy(PDWorld.bot.PRandom)
	PDWorld.bot.setLearn('SARSALearn')
	PDWorld.bot.setLearningRate(0.3)
	PDWorld.bot.setDiscountFactor(0.5)

	agentReward = []
	epochTime = []
	epochStart = -1

	for i in range(500):
		if PDWorld.bot.step():
			epochTime.append(i - epochStart)
			epochStart = i
			agentReward.append(PDWorld.bot.bankAccount)
			PDWorld.bot.bankAccount = 0
			# TODO: plot Q table when terminal state reached
			if not os.path.exists(f'img/term{len(epochTime)}'):
				os.makedirs(f'img/term{len(epochTime)}')
			for j in range(20):
				plotQTable(PDWorld.QTable, j, False, True, f'img/term{len(epochTime)}')
	
	PDWorld.bot.setPolicy(PDWorld.bot.PExploit)
	for i in range(500, 6000):
		if PDWorld.bot.step():
			epochTime.append(i - epochStart)
			epochStart = i
			agentReward.append(PDWorld.bot.bankAccount)
			PDWorld.bot.bankAccount = 0
			# TODO: plot Q table when terminal state reached
			if not os.path.exists(f'img/term{len(epochTime)}'):
				os.makedirs(f'img/term{len(epochTime)}')
			for j in range(20):
				plotQTable(PDWorld.QTable, j, False, True, f'img/term{len(epochTime)}')

	# set utility of invalid operators on table edges
	PDWorld.setEdges()

	if not os.path.exists('img/final'):
		os.makedirs('img/final')

	# save final layers of QTable
	for i in range(20):
		plotQTable(PDWorld.QTable, i, False, True, 'img/final')

	# save graphs of agent reward and epoch time
	title = f'Agent Reward vs Epoch: {PDWorld.bot.getPolicy()} Policy\nLearning Rate = {PDWorld.bot.learningRate}, Discount Factor = {PDWorld.bot.discountFactor}'
	plotLineGraph(agentReward, PDWorld, False, True, 'img/final/reward', title)

	title = f'Epoch Period: {PDWorld.bot.getPolicy()} Policy\nLearning Rate = {PDWorld.bot.learningRate}, Discount Factor = {PDWorld.bot.discountFactor}'
	plotLineGraph(epochTime, PDWorld, False, True, 'img/final/epoch', title)