# Constants and other parameters used by the code
import typing

# Acceptable actions
NORTH = "N"
SOUTH = "S"
EAST = "E"
WEST = "W"
PICKUP = "Pick"
PUTDOWN = "Put"
Actions = [NORTH, SOUTH, EAST, WEST, PICKUP, PUTDOWN]
action_t = typing.NewType("action_t", str)

# Visit all victims or bring them back to the entry
VISIT_GOAL = "Visit"
RETRIEVE_GOAL = "Retrieve"
GoalTypes = [VISIT_GOAL, RETRIEVE_GOAL]

PICKUP_COST = 5
PUTDOWN_COST = 5

# Potential statuses of the agent
SEARCHING = "Searching"
VISITED = "Visited"
CARRYING = "Carrying"
RETRIEVED = "Retrieved"

# Constants used in the map
WALL = "Wall"
FREE = "Free"
ENTRY = "Entry"
