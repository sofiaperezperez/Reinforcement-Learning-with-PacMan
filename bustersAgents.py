from __future__ import print_function
# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from builtins import range
from builtins import object
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters
import numpy as np
import os.path

class NullGraphics(object):
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent(object):
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
    
        return Directions.STOP
    
    def printInfo(self, gameState):
        print("---------------- TICK ", self.countActions, " --------------------------")
        # Map size
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print("Width: ", width, " Height: ", height)
        # Pacman position
        print("Pacman position: ", gameState.getPacmanPosition())
        # Legal actions for Pacman in current position
        print("Legal actions: ", gameState.getLegalPacmanActions())
        # Pacman direction
        print("Pacman direction: ", gameState.data.agentStates[0].getDirection())
        # Number of ghosts
        print("Number of ghosts: ", gameState.getNumAgents() - 1)
        # Alive ghosts (index 0 corresponds to Pacman and is always false)
        print("Living ghosts: ", gameState.getLivingGhosts())
        # Ghosts positions
        print("Ghosts positions: ", gameState.getGhostPositions())
        # Ghosts directions
        print("Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
        # Manhattan distance to ghosts
        print("Ghosts distances: ", gameState.data.ghostDistances)
        # Pending pac dots
        print("Pac dots: ", gameState.getNumFood())
        # Manhattan distance to the closest pac dot
        print("Distance nearest pac dots: ", gameState.getDistanceNearestFood())
        # Map walls
        print("Map:")
        print( gameState.getWalls())
        # Score
        print("Score: ", gameState.getScore())
        
    def chooseAction_best(self, gameState):
        self.countActions = 0
        self.quiero=False
        self.intentos=0
        self.lastmove=0
        self.alternativa=False
        print("lo que quiero:",self.quiero )      
        print("se puede:", self.alternativa)
        print("intentos", self.intentos)
        print("cuantos hay",len(gameState.getLegalActions()) )
        for i in range(0, len(gameState.data.ghostDistances)):
            if gameState.data.ghostDistances[i]==None:
                gameState.data.ghostDistances[i]=1000000
        move=Directions.STOP
        legal=gameState.getLegalActions(0)
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        distances=gameState.data.ghostDistances
        print(distances)
        min_dist=min(distances)
        index_ghost=distances.index(min_dist)
        positions=gameState.getGhostPositions()
        ghostpos=positions[index_ghost]
        
        gx,gy=ghostpos
        px,py=gameState.getPacmanPosition()[0],gameState.getPacmanPosition()[1]
        if px==gx and py==gy:
            
            move=Directions.SOUTH
    
        if self.alternativa==False:
            
            if px==gx:
                if py<gy: #pacman está debajo
                    if Directions.NORTH in legal:
                        move=Directions.NORTH
                    else:
                        if len(gameState.getLegalActions())!=0:
                            move=gameState.getLegalPacmanActions()[random.randint(0,len(gameState.getLegalActions())-1)]
                        else: move = Directions.SOUTH
                        self.lastmove=move
                        self.alternativa=True
                        self.intentos+=1
                        self.quiero=Directions.NORTH
                if py>gy:
                    if Directions.SOUTH in legal:
                        move=Directions.SOUTH
                    else:
                        if len(gameState.getLegalActions())!=0:
                            move=gameState.getLegalPacmanActions()[random.randint(0,len(gameState.getLegalActions())-1)]
                        else: move = Directions.SOUTH
                        
                        self.lastmove=move
                        self.alternativa=True
                        
                        self.intentos+=1
                        self.quiero=Directions.SOUTH
            else:
                if px<gx:
                    if Directions.EAST in legal:
                        move=Directions.EAST
                    else:
                        if len(gameState.getLegalActions())!=0:
                                move=gameState.getLegalPacmanActions()[random.randint(0,len(gameState.getLegalActions())-1)]
                        else: move = Directions.SOUTHove=gameState.getLegalPacmanActions()[random.randint(0,len(gameState.getLegalActions())-1)]
                        self.lastmove=move
                        self.alternativa=True
                        self.intentos+=1
                        self.quiero=Directions.EAST
                if px>gx:
                    if Directions.WEST in legal:
                        move=Directions.WEST
                    else:
                        if len(gameState.getLegalActions())!=0:
                            move=gameState.getLegalPacmanActions()[random.randint(0,len(gameState.getLegalActions())-1)]
                        else: move = Directions.SOUTH
                        self.lastmove=move
                        self.alternativa=True
                        self.intentos+=1
                        self.quiero=Directions.WEST
        elif self.alternativa:
            
            if self.intentos<5 and self.quiero not in legal:
                move=self.lastmove
                self.intentos+=1
                
                self.alternativa=True
            elif self.quiero in legal:
                move=self.quiero
                self.intentos=0
              
                self.alternativa=False
            else:
                if len(gameState.getLegalActions())!=0:
                            move=gameState.getLegalPacmanActions()[random.randint(0,len(gameState.getLegalActions())-1)]
                else: move = Directions.SOUTH
                self.intentos=0
                self.alternativa=False
        
        return move

    def getState(self, gameState):
        walls = gameState.getWalls()
        
        print( "PAred",walls[2][3])
       
        
        element1 =50000
       
        for i in range(0, len(gameState.data.ghostDistances)):
            if gameState.data.ghostDistances[i]==None:
                
                gameState.data.ghostDistances[i]=1000000
                
               
        
        element1= min(gameState.data.ghostDistances)
        print(element1, "distttt")
        if element1 <= 1:
            
            element1 = 0
            
        if element1 != 0:
            
            
            if element1 <=5 and element1 > 1:
                element1 = 1
                
            elif element1 <11 and element1 >= 6:
                
                element1 = 2
                
            elif element1 >= 11:
                element1 =  3
        
        
        
        element2= gameState.getDistanceNearestFood()
        
        if element2!= None:
            if element2 <= 1 :
                element2 = 0
            elif element2 <=8 and element2 > 1:
                element2 = 1
            
            else:
                element2 = 2
        else:
            element2=2
            
       
                        
        best = self.chooseAction_best(gameState)
        print(best)
        if best == "North":
            best = 0
        elif best == "East":
            best = 1
        elif best == "West":
            best = 2
        elif best == "South":
            best = 3
        else:
            best = random.randint(0,2)
        state = [element1, element2, best ]
            
        return(state)
        
class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def update(self, state, action, nextState, reward):
        
        return(0)
        
    def getReward(self, state, action, nextstate):
        
        return(0)
    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move
        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print("---------------- TICK ", self.countActions, " --------------------------")
        # Map size
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print("Width: ", width, " Height: ", height)
        # Pacman position
        print("Pacman position: ", gameState.getPacmanPosition())
        # Legal actions for Pacman in current position
        print("Legal actions: ", gameState.getLegalPacmanActions())
        # Pacman direction
        print("Pacman direction: ", gameState.data.agentStates[0].getDirection())
        # Number of ghosts
        print("Number of ghosts: ", gameState.getNumAgents() - 1)
        # Alive ghosts (index 0 corresponds to Pacman and is always false)
        print("Living ghosts: ", gameState.getLivingGhosts())
        # Ghosts positions
        print("Ghosts positions: ", gameState.getGhostPositions())
        # Ghosts directions
        print("Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
        # Manhattan distance to ghosts
        print("Ghosts distances: ", gameState.data.ghostDistances)
        # Pending pac dots
        print("Pac dots: ", gameState.getNumFood())
        # Manhattan distance to the closest pac dot
        print("Distance nearest pac dots: ", gameState.getDistanceNearestFood())
        # Map walls
        print("Map:")
        print( gameState.getWalls())
        print(isinstance(gameState.getWalls(), list))
        # Score
        print("Score: ", gameState.getScore())
        
        
    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

    def printLineData(self, gameState):
        return "XXXXXXXXXX"
    
    
    


class QLearningAgent(BustersAgent):
    

    #Initialization
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.epsilon = 0.3
        self.alpha = 0.5
        
        self.gamma = 0.8
        self.state = self.getState(gameState)
        state= self.state
        state = BustersAgent.getState(self, gameState)
        self.discount = 0.8
        self.actions = {"North":0, "East":1, "South":2, "West":3}
        if os.path.exists("qtable.txt"):
            print("holaaa")
            self.table_file = open("qtable.txt", "r+")
            self.q_table = self.readQtable()
        else:
            print("holaaa")
            self.table_file = open("qtable.txt", "w+")
            num_states = 48
            #"*** CHECK: NUMBER OF ROWS IN QTABLE DEPENDS ON THE NUMBER OF STATES ***"
            self.initializeQtable(num_states)

    def initializeQtable(self, nrows):
        "Initialize qtable"
        self.q_table = np.zeros((nrows,len(self.actions)))
        print("init", self.q_table)

    def readQtable(self):
        
        "Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)
        #print(q_table, "table") 
        return q_table


    def writeQtable(self):
        "Write qtable to disc"        
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")
        
    def printQtable(self):
        "Print qtable"
        for line in self.q_table:
            print(line)
        print("\n")   
            

    def __del__(self):
        "Destructor. Invokation at the end of each episode"        
        self.writeQtable()
        self.table_file.close()

   
    def computePosition(self,state):
        """
        Compute the row of the qtable for a given state.
        """
        row = state[0] + 16 * state[1] + 4 * state[2] 
       
        return(row)

    def getQValue(self, state, action):

        """
            Returns Q(state,action)
            Should return 0.0 if we have never seen a state
            or the Q node value otherwise
        """
        position = self.computePosition(self.state)
        print(position, "pos")
        action_column = self.actions[action]
        print(action_column, "column")
        return self.q_table[position][action_column]


    def computeValueFromQValues(self, state):
        """
            Returns max_action Q(state,action)
            where the max is over legal actions.  Note that if
            there are no legal actions, which is the case at the
            terminal state, you should return a value of 0.0.
        """
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        if len(legalActions)==0:
            return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, state):
        """
            Compute the best action to take in a state.  Note that if there
            are no legal actions, which is the case at the terminal state,
            you should return None.
        """
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        if len(legalActions)==0:
            return None

        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        for action in legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return random.choice(best_actions)

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """

        # Pick Action
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        action = None

        if len(legalActions) == 0:
                return action

        flip = util.flipCoin(self.epsilon)

        if flip:
            return random.choice(legalActions)
        return self.getPolicy(state)


    def update(self, state, action, nextState, reward):
        """
            The parent class calls this to observe a
            state = action => nextState and reward transition.
            You should do your Q-Value update here

        Q-Learning update:

        if terminal_state:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + 0)
        else:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + self.discount * max a' Q(nextState, a'))
        
        """
        index=self.actions[action]
        row=self.computePosition(state)
        print(index, row,0)
        print("table", self.q_table)
        actual = self.q_table[row][index]
            
        if state[0] == 0:
            
            q = (1- self.alpha) * actual + self.alpha * self.getReward( state, action, nextState)
           
        else:
            print(nextState)
            print("else", self.computePosition(nextState))
            nextrow=self.q_table[self.computePosition(nextState)]
            
            q = (1- self.alpha) * actual + self.alpha * (self.getReward( state, action, nextState) + self.discount * max(nextrow))      
            
        
        self.q_table[row][index]=q
        print("update", q)
        print(self.q_table, "table") 
        
    def getPolicy(self, state):
        "Return the best action in the qtable for a given state"        
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        "Return the highest q value for a given state"        
        return self.computeValueFromQValues(state)

    def getReward(self, state, action, nextstate):
        "Return the obtained reward"
        reward = 0
        print(state, "state")
        print(nextstate,11111111)
       
        if state[0] == 0 or state[1] == 0:
            reward = 0.75
        
        elif nextstate[1] == 0 or nextstate[0] == 0:
            reward = 0.75
            
        if state[2] == action and state[0] <= 1:
            reward = 1 
        
        
       
           
      
        
        print(reward, "reward")
        return(reward)


