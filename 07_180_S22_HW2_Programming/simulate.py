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
from params import *
import graphics

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

    def initialize(self, map, goalType, useGraphics = False, title="S&R", speed=0.2):
        self._map = map
        self._goalType = goalType
        self._victims = map.getVictims()[:] # Copy list
        self._visited = [False] * len(map.getVictims())
        self._agentLocn = map.getEntry()
        self._holding = None
        self._cost = 0
        if (useGraphics):
            self._graphics = graphics.SAR_Graphics(map, title=title)
            self._speed = speed

    def __init__(self, map, goalType, useGraphics = False, title="S&R", speed=0.2):
        self.initialize(map, goalType, useGraphics, title=title, speed=speed)
        
    # Cost of moving into the next agent location,
    #  with or without carrying a victim
    def _moveCost(self):
        cost = self._map.getCellL(self._agentLocn).getObstruction()
        return (cost if not self._holding else cost*cost)

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
                    return (self._agentLocn, PICKUP_COST)

        # Can put down victim if at that location and holding someone
        elif (action == PUTDOWN and self._holding):
            for victim in self._victims:
                if (self._graphics):
                    self._graphics.update_msg("Putting down victim at %s" % self._agentLocn)
                else: print("Putting down victim at %s" %self._agentLocn)
                self._holding = None
                self._victims = [self._agentLocn if not vict else vict
                                 for vict in self._victims]
                return (self._agentLocn, PUTDOWN_COST)
        else:
            self._agentLocn = self._map.move(action, self._agentLocn.row,
                                             self._agentLocn.col)
            cost = self._moveCost()
            #print("%s %s %d" %(self._agentLocn, action, cost))
            try:
                self._visited[self._victims.index(self._agentLocn)] = True
                if (self._graphics):
                    self._graphics.update_msg("Found victim at %s" %self._agentLocn)
                else: print("Found victim at %s" %self._agentLocn)
            except ValueError:
                pass
            return (self._agentLocn, cost)

    def doPlan (self, plan):
        if (self._graphics): graphics.sleep(1)
        for idx in range(len(plan)):
            action = plan[idx]
            nextLocn, localCost = self.doAction(action)
            self._cost += localCost
            if (self._graphics):
                self._graphics.update_map(self._agentLocn, self._victims)
                self._graphics.update_cost(self._cost)
                graphics.sleep(self._speed)
        if (self._goalType == VISIT_GOAL):
            #success = reduce(andFn, self._visited) # Have visited them all?
            success = reduce(orFn, self._visited) # Have visited at least one?
        elif (self._goalType == RETRIEVE_GOAL):
            """
            # Have all victims been retrieved?
            success = reduce(andFn, [vict == self._map.getEntry()
                                     for vict in self._victims])
            """
            # Have at least one victim been retrieved?
            success = reduce(orFn, [vict == self._map.getEntry()
                                     for vict in self._victims])
        else: success = False
        if (self._graphics):
            self._graphics.update_cost(self._cost)
            self._graphics.update_msg(("SUCCESS!" if success else "FAILED :("))
            graphics.sleep(2)
        return (self._cost if success else None)

