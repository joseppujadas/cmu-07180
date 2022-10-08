import argparse
import sys
import readMap
import search
import SAR
import simulate
from params import *

simSpeed = 0.1 # Speed to run the simulation graphics, in seconds

def simulate_search(map, searchType, goalType, useGraphics, debugging):
    print("\n%s search with %s goal" %(searchType, goalType))
    if not searchType in search.SearchTypes:
        raise ValueError("Invalid Search Type")
    searchInstance = search.Search(searchType, Actions, debugging)
    s0 = SAR.createStartState(map, goalType)
    path, nodeCount, estCost = searchInstance.doSearch(s0)
    if path:
        if searchType in search.USearchTypes:
            print("Node Count: %d, Path (%d): %s" %(nodeCount, len(path), path))
        else:
            print("Node Count: %d, Path (%d): Cost: %d: %s"
                  %(nodeCount, len(path), estCost, path))
        simr = simulate.Simulator(map, goalType, useGraphics, title="S&R: "+searchType, speed=simSpeed)
        cost = simr.doPlan(path)
        if cost: print("Simulation cost: %s" %cost)
        else: print("PLAN FAILED TO ACHIEVE %s GOALS" %goalType)
    else:
        print("%s: Node Count: %d, NO PATH FOUND" %(searchType, nodeCount))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--map', nargs='?')
    parser.add_argument('--search', nargs='?')
    parser.add_argument('--goal', nargs='?')
    parser.add_argument('--no-graphics', action='store_true')
    parser.add_argument('--debugging', action='store_true')
    args = parser.parse_args()
    use_graphics = not args.no_graphics

    if (args.goal and not args.goal in GoalTypes):
        raise Exception("'%s' not a valid goal type; Valid types are %s" %(args.goal, GoalTypes))
    if (args.search and not args.search in search.SearchTypes):
        raise Exception("'%s' not a valid goal type; Valid types are %s" % (args.search, search.SearchTypes))

    map_files = ["maps/simple.map", "maps/simple_v2.map", "maps/medium.map", "maps/medium_v2.map", "maps/medium_v4.map"]
    for map_file in ((args.map,) if args.map else map_files):
        print("Reading map file '%s'" % map_file)
        m = readMap.read(map_file)
        for goalType in ((args.goal,) if args.goal else GoalTypes):
            for searchType in ((args.search,) if args.search else search.SearchTypes):
                plan = simulate_search(m, searchType, goalType,
                                       use_graphics, args.debugging)

