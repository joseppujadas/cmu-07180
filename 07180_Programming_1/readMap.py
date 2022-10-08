"""
readMap.py

Read and parse a text file representing a map into a Map data structure
Map is a grid, where each cell is either wall or free
In the map file, a '#' represents a wall; a free cell can be either
 a space, a number from 1-9 (obstruction cost of traversing that cell),
 an 'E' (the entry to the building) or 'V' (a victim is in that cell).
Obstruction cost of a space is 1, by default.
There should be exactly one cell labeled 'E' and it should be adjacent
 to the outer boundary of the map
The first lines of a map file can be comments, indicated with '%'
Location (0,0) is the upper right of the map
"""
from typing import List
from map import *


def check_map(lines: List[str]) -> bool:
    """
    helper function for parser by catching malformed maps (multiple entries, entry not adjacent to border walls,
    no victims, border not contiguous, etc.)
    :param lines: map file
    :return: boolean
    """
    hasEntry, hasVictim = False, False
    for line in lines:
        if line[0] == "\n" or line[0] == "%":
            continue
        for char in line:
            if char == "E":
                if hasEntry:
                    return False
                else:
                    hasEntry = True
            elif char == "V" and not hasVictim:
                hasVictim = True
    if not hasEntry or not hasVictim:
        return False
    return True


def parse(lines: List[str]) -> List[Cell]:
    if not check_map(lines):
        raise ValueError("map file is malformed")
    line_no = 0
    row = 0
    cells = []
    for line in lines:
        line_no += 1
        if line[0] == "\n" or line[0] == "%":
            continue
        col = -1
        foundWall = False
        cell = None
        for char in line:
            col += 1
            # Process until the first wall character, then start adding cells
            if char == "#":
                cell = Wall(row, col)
                foundWall = True
            elif not foundWall or char == "\n":
                continue
            elif char == "E":
                cell = Entry(row, col)
            else:
                cell = Free(row, col)
                if char == "V":
                    cell.setVictim()
                elif str.isdigit(char):
                    cell.setObstruction(int(char))
            if cell:
                cells.append(cell)
        row += 1
    return cells


def read(filename: str) -> Map:
    with open(filename) as f:
        lines = f.readlines()
        cells = parse(lines)
        return Map(cells)
