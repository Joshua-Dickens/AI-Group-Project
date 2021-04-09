import random

# Initial States
ij = [5, 1] # Current Location of the robot
x = 0 # If the Robot is carrying a box, 0 is no, 1 is yes
a = 0 # Dropoff Point A
b = 0 # Dropoff Point B
c = 0 # Dropoff Point C
d = 8 # Pickup Point D
e = 8 # Pickup Point E
f = 0 # Dropoff Point F

# Terminal States a.k.a the goal state
termX = 0
termA = 4
termB = 4
termC = 4
termD = 0
termE = 0
termF = 4

# Dropoff Coordinates
coordsA = [1,1]
coordsB = [1,5]
coordsC = [3,3]
coordsF = [5,5]

# Pickup Coordinates
coordsD = [4,2]
coordsE = [3,5]

# Choice Array False means not possible, True is possible [Move North, Move West, Move East, Move South, Pickup, Dropoff]
choices = [True, False, True, False, False, False]

# Restart the game
def restart():
    ij[0] = 5
    ij[1] = 1
    x = 0 
    a = 0 
    b = 0 
    c = 0 
    d = 8 
    e = 8 
    f = 0 


# Assigns a reward based on action taken, moving is -1 and picking up or dropping off blocks are worth 13
def giveReward(action):
    if(action == "Movement North" or action == "Movement West" or action == "Movement South" or action == "Movement East"):
        return -1
    else:
        return 13

# Checks the current state against goal state. Returns true if at goal state and false if not at goal
def checkStates():
    if(x == termX and a == termA and b == termB and c == termC and d == termD and e == termE and f == termF):
        return True
    else:
        return False

# Establishes all currently possible choices
def updateChoices():
    choices[0] = ij[0] != 1
    choices[1] = ij[1] != 1
    choices[2] = ij[1] != 5
    choices[3] = ij[0] != 5
    choices[4] = ((ij == coordsD and d > 0) or (ij == coordsE and e > 0) and x == 0)
    choices[5] = ((ij == coordsA and a < 4) or (ij == coordsB and b < 4) or (ij == coordsC and c < 4) or (ij == coordsF and f < 4) and x == 1)

# Adjusts state when pickup occurs based on current location
def pickup():
    x = 1
    if(ij == coordsD):
        d -= 1
    else:
        e -= 1

# Adjust state when dropoff occurs based on current location
def dropoff():
    x = 0
    if(ij == coordsA):
        a += 1
    elif(ij == coordsB):
        b += 1
    elif(ij == coordsC):
        c += 1
    else:
        f += 1

# Apply movement
def movement(movement):
    if movement == "Movement North":
        ij[0] = ij[0] - 1
    elif movement == "Movement South":
        ij[0] = ij[0] + 1
    elif movement == "Movement East":
        ij[1] = ij[1] + 1
    else:
        ij[1] = ij[1] - 1

# PRandom choice maker
def PRandom():
    if choices[4]:
        return "Pickup"
    elif choices[5]:
        return "Dropoff"
    else:
        choice = random.randint(0, 3)
        while(choices[choice] == False):
            choice = random.randint(0, 3)
        if choice == 0:
            return "Movement North"
        elif choice == 1:
            return "Movement West"
        elif choice == 2:
            return "Movement East"
        else:
            return "Movement South"


