"""
SAR.py
Basic implementation for the search and rescue domain
Students need to...
- extend State.moveActionCost and tryToMove
- implement tryToPick and tryToPut
- implement manhattan distance function
- implement heuristic for retrieving a victim
- extend the implementation to handle multiple victims (where the goal is just
  to visit/retrieve one of them)
"""
import search
from params import *

def manhattan(l0, l1):
    """
    Return the manhattan distance between locations 0 and 1.
    l1 and l2 are Locn objects (defined in map.py)
    """
    # BEGIN STUDENT CODE FOR PROBLEM 1
    # END STUDENT CODE
    return 0

class SAR_State(search.State):
    def __init__(self, map, locn, status, victims, goalType):
        self.map = map
        self.locn = locn
        self.status = status # See params.py for the available statuses
        self.victims = victims
        self.goalType = goalType

    def __hash__(self):
        return (hash(self.locn) + 13 * hash(self.map) +
                173 * sum([hash(item) for item in self.victims]) +
                19 * hash(self.status))

    def __eq__(self, other):
        return (other != None and isinstance(other, SAR_State) and
                self.map == other.map and self.locn == other.locn and
                self.victims == other.victims and self.status == other.status and
                self.goalType == other.goalType)

    def __repr__(self):
        """
        This function is called when you print a State.
        Feel free to edit if you prefer the information in a different form
        """
        return ("<State [%d, %d] (%s) %s>"
                % (self.locn.row, self.locn.col, self.status, self.victims))

    def act(self, action):
        """
        Returns the state and cost of doing the action, or (None, 0) if action not legal
        """
        if (action == PICKUP): return self.tryToPick()
        elif (action == PUTDOWN): return self.tryToPut()
        else: return self.tryToMove(action)

    def moveActionCost(self):
        # BEGIN STUDENT CODE FOR PROBLEM 2: extend for when carrying a victim
        # END STUDENT CODE FOR PROBLEM 2
        cellCost = self.map.getCellCost(self.locn)
        return cellCost

    def tryToMove(self, action):
        """
        This function returns the SAR_State that results from performing the given movement
        (NORTH, SOUTH, EAST, WEST) and the cost of that action (the moveActionCost)

        FOR PROBLEM 1 - implement for moving to a new location
          Return the new state and cost if the action succeeds in moving to a new location
          Make sure to update the agent's status if the move visits a victim
          Note: The cost of a move action is the cost of the state being moved into
        FOR PROBLEM 3 - Extend for multiple victims, if not already implemented
        """
        newLocn = self.map.move(action, self.locn.row, self.locn.col)
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        return (None, 0)


    def tryToPick(self):
        """
        This function returns the SAR_State that results from performing the
          PICKUP action and its cost

        FOR PROBLEM 2 - implement for picking up a victim:
          Return the new state and cost if the PICKUP action is legal in the current state, o/w None
          Make sure to update the agent's status in the new state
        FOR PROBLEM 3 - extend for handling multiple victims, if not already
        """
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        return (None, 0)

    def tryToPut(self):
        """
        This function returns the SAR_State that results from performing the
          PICKUP action and its cost

        Implement for putting down a victim:
          Return the new state and cost if the PUTDOWN action is legal in the current state, o/w None
          Make sure to update the agent's status in the next state
        """
        # BEGIN STUDENT CODE
        # END STUDENT CODE
        return (None, 0)

    def isGoal(self):
        """
        This function determines whether the State is a goal state
        """
        return ((self.goalType == VISIT_GOAL and self.status == VISITED) or
                (self.goalType == RETRIEVE_GOAL and self.status == RETRIEVED))

    def costToGoal(self):
        """
        Return the heuristic estimate of the cost from the given state to a goal state
        """
        if (self.goalType == VISIT_GOAL):
            """
            STUDENT CODE FOR PROBLEM 1 - write an admissible heuristic for
              the cost of reaching a victim
            STUDENT CODE FOR PROBLEM 3 - extend heuristic to handle a list of victims;
              The agent should visit the closest victim.
              Make sure that the heuristic is still admissible
            """
            # BEGIN STUDENT CODE
            # END STUDENT CODE
            pass
        elif (self.goalType == RETRIEVE_GOAL):
            """
            STUDENT CODE FOR PROBLEM 2 - write an admissible heuristic for
              retrieving a victim.
              General strategy is to estimate the cost for reaching the victim
              (if not already being carried) and then carrying them to the entry
            STUDENT CODE FOR PROBLEM 3 - extend to handle a list victims
              The agent should retrieve the victim that costs the least to find and retrieve
            """
            # BEGIN STUDENT CODE
            # END STUDENT CODE
            pass
        return 0

def createStartState(map, goalType):
    return SAR_State(map, map.getEntry(), SEARCHING, map.getVictims(), goalType)
