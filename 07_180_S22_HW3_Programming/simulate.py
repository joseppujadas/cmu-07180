"""
simulate.py

Simulate plan execution
1) Initialize the simulation, providing an initial state and
   a goalType(either visit all victims or deliver victims to entry)
2) Execute an individual action; returns a (nextLocn, cost) tuple
OR
3) Execute a plan (list of search.actions);
   Returns the cost of the plan or None, if it fails to achieve
   the goal
"""

from functools import reduce
import math
import random
from params import *
import graphics
import random
from SAR_MDP import GOAL_REWARD

andFn = (lambda a, b: a and b)
orFn = (lambda a, b: a or b)

class Simulator:
    _map = None
    _goalType = None
    _victims = []
    _agentLocn = None
    _holding = None
    _cost = 0
    _graphics = False
    _speed = 0.2 # Speed at which to run the simulation graphics
    _probabilistic = False
    _visit_reward = GOAL_REWARD
    _retrieve_reward = GOAL_REWARD

    def initialize(self, map, goalType, useGraphics = False, title="S&R", speed=0.2, probabilistic=False):
        self._map = map
        self._goalType = goalType
        self._victims = map.getVictims()[:] # Copy list
        self._visited = [False] * len(map.getVictims())
        self._agentLocn = map.getEntry()
        self._holding = None
        self._cost = 0
        self._probabilistic = probabilistic
        if (useGraphics):
            self._graphics = graphics.SAR_Graphics(map, title=title)
            self._speed = speed

    def __init__(self, map, goalType, useGraphics = False, title="S&R", speed=0.2, probabilistic=False):
        self.initialize(map, goalType, useGraphics, title=title, speed=speed, probabilistic=probabilistic)
        
    # Cost of moving into the next agent location,
    #  with or without carrying a victim
    def _moveCost(self):
        cost = self._map.getCellL(self._agentLocn).getObstruction()
        return (cost if not self._holding else cost*cost)

    def _leftCell(self, action):
        row = self._agentLocn.row; col = self._agentLocn.col
        row += (0 if action in (NORTH, SOUTH) else 1 if action == WEST else -1)
        col += (0 if action in (WEST, EAST) else 1 if action == SOUTH else -1)
        return self._map.getCell(row, col)

    def _rightCell(self, action):
        row = self._agentLocn.row;
        col = self._agentLocn.col
        row += (0 if action in (NORTH, SOUTH) else -1 if action == WEST else 1)
        col += (0 if action in (WEST, EAST) else -1 if action == SOUTH else 1)
        return self._map.getCell(row, col)

    def _forwardCell(self, action):
        row = self._agentLocn.row; col = self._agentLocn.col
        row += (0 if action in (WEST, EAST) else 1 if action == SOUTH else -1)
        col += (0 if action in (NORTH, SOUTH) else -1 if action == WEST else 1)
        return self._map.getCell(row, col)

    def _moveProbabilistic(self, action):
        slip_cost = math.sqrt(self._moveCost())
        slip = 0.05*slip_cost; stay = 0.01*slip_cost
        leftCell = self._leftCell(action); rightCell= self._rightCell(action); forwardCell = self._forwardCell(action)
        forward = 1 - 2*slip - stay
        if (leftCell.isWall()): stay += slip
        if (rightCell.isWall()): stay += slip
        if (forwardCell.isWall()): stay += forward
        moves = []; probs = []
        if (not forwardCell.isWall()): moves.append(forwardCell.locn); probs.append(forward)
        if (not leftCell.isWall()): moves.append(leftCell.locn); probs.append(slip)
        if (not rightCell.isWall()): moves.append(rightCell.locn); probs.append(slip)
        moves.append(self._agentLocn); probs.append(stay)
        return random.choices(moves, probs, k=1)[0]

    def doAction (self, action):
        if (not action in Actions):
            raise Exception("Unknown action  %s" %action)
        # Can pick up victim if at that location and not holding anyone
        elif (action == PICKUP and not self._holding):
            for victim in self._victims:
                if (self._agentLocn == victim):
                    if (self._graphics):
                        self._graphics.update_msg("Picking up victim at %s" %self._agentLocn)
                    else: print("Picking up victim at %s" %self._agentLocn)
                    self._holding = victim
                    self._victims = [None if vict == victim else vict
                                     for vict in self._victims]
                    return (self._agentLocn, PICKUP_COST, False, True)
            return (self._agentLocn, PICKUP_COST, False, False)

        # Can put down victim if at that location and holding someone
        elif (action == PUTDOWN and self._holding):
            for victim in self._victims:
                if (self._graphics):
                    self._graphics.update_msg("Putting down victim at %s" % self._agentLocn)
                else: print("Putting down victim at %s" %self._agentLocn)
                self._holding = None
                self._victims = [self._agentLocn if not vict else vict
                                 for vict in self._victims]
                return (self._agentLocn, PUTDOWN_COST, False, False)
            return (self._agentLocn, PUTDOWN_COST, False, False)
        else:
            cost = self._moveCost()
            #print("%s %s %d" %(self._agentLocn, action, cost))
            if (self._probabilistic):
                self._agentLocn = self._moveProbabilistic(action)
            else:
                self._agentLocn = self._map.move(action, self._agentLocn.row, self._agentLocn.col)
            try:
                idx = self._victims.index(self._agentLocn) # Will raise an error if no victim at that location
                visited = not self._visited[idx] # Give reward only first time being visited
                self._visited[idx] = True
                if (self._graphics):
                    self._graphics.update_msg("Found victim at %s" %self._agentLocn)
                else: print("Found victim at %s" %self._agentLocn)
            except ValueError:
                visited = False
                pass
            if visited: cost -= self._visit_reward
            return (self._agentLocn, cost, visited, self._holding != None)

    def _goalAchieved(self):
        if (self._goalType == VISIT_GOAL): # Have visited one them?
            return reduce(orFn, self._visited)
        elif (self._goalType == RETRIEVE_GOAL):
            return reduce(orFn, [vict == self._map.getEntry()
                                 for vict in self._victims])
        else: return False

    def _updateGraphicsMove(self):
        self._graphics.update_map(self._agentLocn, self._victims)
        self._graphics.update_cost(self._cost)
        graphics.sleep(self._speed)

    def _updateGraphicsEnd(self):
        self._graphics.update_cost(self._cost)
        self._graphics.update_msg(("SUCCESS!" if self._goalAchieved() else "FAILED :("))
        graphics.sleep(2)

    def doPlan (self, plan):
        if (self._graphics): graphics.sleep(1)
        for idx in range(len(plan)):
            action = plan[idx]
            nextLocn, localCost = self.doAction(action)
            self._cost += localCost
            if (self._graphics): self._updateGraphicsMove()
        # Add in cost for last state
        self._cost += self._moveCost()
        if (self._graphics): self._updateGraphicsEnd()
        return (self._cost if self._goalAchieved() else None)

    def doPolicy (self, executor, maxSteps):
        if (self._graphics): graphics.sleep(1)
        t = 0
        # Fail if goal not achieved after executing MAX_STEPS actions
        while not self._goalAchieved() and t < maxSteps:
            action = executor.choose_action()
            if (not action): action = random.choice(Actions)
            next_locn, localCost, foundVictim, isHolding = self.doAction(action)
            executor.update_state(action, next_locn)
            #print(cur_state, action, next_locn, localCost)
            self._cost += localCost
            t += 1
            if (self._graphics): self._updateGraphicsMove()
        # Add in cost for last state
        self._cost += self._moveCost()
        if (self._graphics): self._updateGraphicsEnd()
        return (self._cost if self._goalAchieved() else None)
