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

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Map)
            and self.victims == other.victims
            and self.grid == other.grid
            and self.entry == other.entry
        )

    def __hash__(self) -> int:
        return hash(tuple(self.victims)) + 181 * hash(self.entry)

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

    def numRows(self): return len(self.grid)
    def numCols(self): return len(self.grid[0])

    # returns the Locn of the map's entry
    def getEntry(self) -> Locn:
        return self.entry

    # returns a list of victims. note that victims are represented by a Locn object that corresponds to their location
    # on the map
    def getVictims(self) -> List[Locn]:
        return self.victims

    # Note that these functions can return None since some of the cells in the grid are None
    def getCell(self, row: int, col: int) -> Cell:
        """
        Given a row and a column in the grid, return the cell at that row and column.
        Don't worry about out-of-bounds accesses.
        """
        return self.grid[row][col]

    def getCellL(self, locn: Locn) -> Cell:
        """
        Given a Locn object, return the cell in the grid at the location represented by the Locn object.
        Don't worry about out-of-bounds-accesses
        """
        return self.grid[locn.getRow()][locn.getCol()]

    # checks if there is a victim at the given row and col
    def isVictim(self, row: int, col: int) -> bool:
        return self.getCell(row, col).isVictim()

    # check if it is possible to move in a given direction at the specified row and col
    def canMove(self, dir: action_t, row: int, col: int) -> bool:
        cell = self.grid[row][col]
        return False if cell.isWall() else self.move(dir, row, col) != cell.getLocn()

    def getCellCost(self, locn):
        return self.getCellL(locn).getObstruction()

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
