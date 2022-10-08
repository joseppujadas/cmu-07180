"""
map.py

Map representation for search and rescue domain
A map is composed of cells, which can be either 'Free', 'Wall' or 'Entry'.
Free cells can have an obstruction cost (integer 1-9) and whether
 a victim is in that cell
Exactly one cell in a map is the Entry point to the building,
 and it needs to be adjacent to the outer boundary of the map
Locn is the (row, col) location of a cell
"""
from typing import List, Optional, Dict, Tuple
from params import *


# The Locn class simply represents a location in the map with a row and a column
class Locn:
    # this function initializes a new Locn
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    # this function is used to hash a Locn. you do not need to know the specifics behind it for this course.
    def __hash__(self) -> int:
        return self.row * 59 + self.col

    # this function is for checking equality between one Locn and another
    def __eq__(self, other) -> bool:
        return (
            other is not None
            and isinstance(other, Locn)
            and self.row == other.row
            and self.col == other.col
        )

    # this function is for checking inequality between one Locn and another
    def __ne__(self, other) -> bool:
        return not self == other

    # this function determines what is displayed when you try to print a Locn
    def __repr__(self) -> str:
        return "<Locn [%d, %d]>" % (self.row, self.col)

    def getRow(self) -> int:
        return self.row

    def getCol(self) -> int:
        return self.col


"""
a Cell is defined as having a Locn and a type
a Cell's type can be Wall, Free, or Entry
a Wall Cell represents a Wall on the map
a Free Cell represents a Free space on the map and has an obstruction cost associated with it
an Entry Cell represents the entry on the map
"""


class Cell:
    def __init__(self, row: int, col: int):
        self.locn = Locn(row, col)
        self.type = None

    def __hash__(self) -> int:
        return 13 * hash(self.type) + hash(self.locn)

    def __eq__(self, other) -> bool:
        return other is not None and self.locn == other.locn and self.type == other.type

    def __ne__(self, other) -> bool:
        return not self == other

    def __repr__(self) -> str:
        return "<Cell %s at [%d, %d]>" % (self.type, self.locn.row, self.locn.col)

    # returns the Locn object at this grid location
    def getLocn(self) -> Locn:
        return self.locn

    # these functions check whether the cell is a WALL, FREE, or ENTRY respectively
    def isWall(self) -> bool:
        return self.type == WALL

    def isFree(self) -> bool:
        return self.type == FREE

    def isEntry(self) -> bool:
        return self.type == ENTRY


# a Free Cell represents a Free space on the map and has an obstruction cost associated with it (default 1)
# self.victim keeps track of whether or not there is a victim (represented by a Locn)
class Free(Cell):
    obstruction: int
    victim: bool

    def __init__(self, row: int, col: int):
        Cell.__init__(self, row, col)
        self.type = FREE
        self.obstruction = 1
        self.victim = False

    def __repr__(self) -> str:
        return "<Cell %s at [%d, %d] with obstruction cost %d>" % (
            self.type,
            self.locn.row,
            self.locn.col,
            self.obstruction,
        )

    def setObstruction(self, obstruction: int):
        self.obstruction = obstruction

    # returns the obstruction cost of the cell (a value from 1-9)
    # note that the entry cell will always have obstruction cost 1
    def getObstruction(self) -> int:
        return self.obstruction

    def setVictim(self):
        self.victim = True

    # returns whether or not there is a victim at the cell
    def isVictim(self) -> bool:
        return self.victim


# an Entry Cell represents the entry on the map
class Entry(Free):
    def __init__(self, row: int, col: int):
        Free.__init__(self, row, col)
        self.type = ENTRY


# a Wall Cell represents a Wall on the map
class Wall(Cell):
    def __init__(self, row: int, col: int):
        Cell.__init__(self, row, col)
        self.type = WALL


class Map:
    victims: List[Locn]
    grid: List[List[Optional[Cell]]]
    entry: Optional[Locn]

    def __init__(self, cells: List[Cell]):
        self.victims = (
            []
        )  # List of Locn's where there are victims. Note that victims are represented by Locns.
        self.grid = [[]]  # 2D list representing a grid of Cells
        self.entry = None  # Locn representing the entry
        self.processCells(cells)

    # this is for setting up the map
    def processCells(self, cells: List[Cell]):
        # Find the extent of the grid
        rowMax = 0
        colMax = 0
        for cell in cells:
            rowMax = max(rowMax, cell.locn.row)
            colMax = max(colMax, cell.locn.col)

        self.grid = []
        for i in range(rowMax + 1):
            self.grid.append([None] * (colMax + 1))

        for cell in cells:
            self.grid[cell.locn.row][cell.locn.col] = cell
            if cell.isEntry():
                self.entry = cell.locn
            if cell.isFree() and cell.isVictim():
                self.victims.append(cell.locn)

    # returns the Locn of the map's entry
    def getEntry(self) -> Locn:
        return self.entry

    # returns a list of victims. note that victims are represented by a Locn object that corresponds to their location
    # on the map
    def getVictims(self) -> List[Locn]:
        return self.victims

    def getCell(self, row: int, col: int) -> Cell:
        """
        Given a row and a column in the grid, return the cell at that row and column.
        Don't worry about out-of-bounds accesses.
        """
        # STUDENT CODE FOR PROBLEM 2
        return self.grid[row][col];

    def getCellL(self, locn: Locn) -> Cell:
        """
        Given a Locn object, return the cell in the grid at the location represented by the Locn object.
        Don't worry about out-of-bounds-accesses
        """
        # STUDENT CODE FOR PROBLEM 2
        return self.grid[locn.row][locn.col];

    # checks if there is a victim at the given row and col
    def isVictim(self, row: int, col: int) -> bool:
        return self.getCell(row, col).isVictim()

    # check if it is possible to move in a given direction at the specified row and col
    def canMove(self, dir: action_t, row: int, col: int) -> bool:
        cell = self.grid[row][col]
        return False if cell.isWall() else self.move(dir, row, col) != cell.getLocn()

    # return the resulting Locn of attempting to move in the specified direction at row and col
    # note that if the move is invalid, this returns the current Locn
    def move(self, dir: action_t, row: int, col: int) -> Locn:
        cell = self.grid[row][col]
        row += 1 if dir == SOUTH else -1 if dir == NORTH else 0
        col += 1 if dir == EAST else -1 if dir == WEST else 0
        nextCell = self.grid[row][col]
        return (cell if nextCell.isWall() else nextCell).getLocn()

    def display(self):
        for row in range(len(self.grid)):
            for col in range(len(self.grid[0])):
                cell = self.getCell(row, col)
                if cell == None:
                    print(" ", end="")
                elif cell.isWall():
                    print("#", end="")
                elif cell.isEntry():
                    print("E", end="")
                else:  # Free
                    if cell.isVictim():
                        print("V", end="")
                    elif cell.getObstruction() > 1:
                        print("%d" % cell.getObstruction(), end="")
                    else:
                        print(" ", end="")
            print("")


def obstructionAddition(cell1: Cell, cell2: Cell) -> int:
    """
    Given two cells, return -1 if either of them is not free. Otherwise, return the sum of their obstruction costs.
    For the sake of simplicity, we do not count Entry cells as being Free even though Entry cells are technically
    special Free cells.
    """
    # STUDENT CODE FOR PROBLEM 1
    if not cell1.isFree() or not cell2.isFree():
        return -1;
    return cell1.obstruction + cell2.obstruction;



def victimSum(victim_map: Map) -> Tuple[int, int]:
    """
    Given a Map object, sum the rows and columns of all of the victims in the Map and return them as a tuple.

    For example, if there were two victims, one at row 3 column 4 and one at row 2 column 2, return (5, 6)
    """
    # STUDENT CODE FOR PROBLEM 3
    rowSum = 0;
    colSum = 0;
    for loc in victim_map.victims:
        rowSum += loc.row;
        colSum += loc.col;
    return rowSum, colSum;


class Agent:
    current_map: Map
    locn: Locn
    visited_victims: Dict[Locn, bool]

    def __init__(self, current_map: Map):
        """
        current_map is a Map object that represents the Map that the Agent is currently on
        locn is a Locn object that represents the Agent's current location on the Map
        visited_victims is a dictionary that maps each victim's Locn to a boolean flag that represents if the Agent has visited them
        path is a chronological list of Locns that the Agent has been to
        """
        self.current_map = current_map
        self.locn = Locn(0, 0)
        self.locn.row = current_map.getEntry().row
        self.locn.col = current_map.getEntry().col
        self.visited_victims = {}
        self.path = [current_map.getEntry()]

        for victim in current_map.getVictims():
            # it's ok to assume that there is no victim at the Entry
            self.visited_victims[victim] = False

    def move(self, new_locn: Locn):
        """
        Move the Agent to a new location represented by new_locn
        """
        # update the Agent's location
        self.locn.row = new_locn.getRow()
        self.locn.col = new_locn.getCol()

        # add our new location to the path
        self.path.append(new_locn)

        # did we visit any new victims?
        for victim_locn in self.visited_victims:
            if self.locn == victim_locn:
                self.visited_victims[victim_locn] = True

    def allVisited(self) -> bool:
        """
        Check if we've visited all the victims
        Return True if we have and False if we have not
        """
        # we must have visited all the victims if there are no Falses in the dictionary
        for vic in self.visited_victims:
            if not self.visited_victims[vic]:
                return False
        return True
