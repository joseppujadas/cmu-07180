"""
search.py
Implementation of uninformed search and framework for heuristic search.
A Node is used to represent the search graph, and a State is the state of a search node.
The Search class encapsulates the whole search space
"""
from collections import deque
from heapq import heappush, heappop
from functools import reduce

# Uninformed search algorithms
DFS = 'DFS'
BFS = 'BFS'
USearchTypes = [DFS, BFS]

# Cost-based search algorithms
UCS = 'UCS'
GREEDY = 'Greedy'
ASTAR = 'A*'
CSearchTypes = [UCS, GREEDY, ASTAR] # Greedy is also called best-first

SearchTypes = USearchTypes + CSearchTypes

class State:
    def __init__(self):
        pass

    # The hash function is used efficiently determine if a state has already been searched
    def __hash__(self): # Must be implemented for the specific domain
        raise Exception("__hash__ not implemented")
        return 1

    def __eq__(self, other): # Must be implemented for the specific domain
        raise Exception("__eq__ not implemented")
        return False
    def __ne__(self, other): return not self == other

    # This function is called when you try to print a State.
    def __repr__(self): # Should be extended for the specific domain
        return "<State %s"

    # Given the action, return a new state and the cost of performing the action
    # If the action cannot be performed in the state, return (None 0)
    def act(self, action):
        return (None, 0)

    # This function determines whether or not the State is a goal state
    def isGoal(self):
        return False

    # Return the heuristic estimate of the cost from the given state to a goal state
    def costToGoal(self):
        return 0

class Node:
    """
    This class, and the following functions, do not need to be extended,
    but it is not prohibited to do so.
    """
    parent = None
    state = None
    action = None
    children = None
    index = 0
    # Needed for the cost-based search methods (UCS, Greedy, A*)
    removed = False
    g = 0
    h = 0
    index_g = 0 # Global value - last node's index

    def __init__(self, state):
        self.state = state
        self.children = []
        self.index = self.incCount()

    def incCount(self):
        Node.index_g += 1
        return Node.index_g

    def addChild(self, childState, action):
        childNode = Node(childState)
        self.children.append(childNode)
        childNode.parent = self
        childNode.action = action
        return childNode

class Search:
    debugging = False
    actions = None
    searchType = None

    def __init__(self, searchType, actions, debugging=False):
        self.searchType = searchType
        self.actions = actions
        self.debugging = debugging

    def generatePath(self, node):
        path = []
        while node.parent:
            path = [node.action] + path
            node = node.parent
        return path

    # For dealing with DFS and BFS
    def addToDeque(self, node, dq, expanded):
        expanded.add(node.state)
        if (self.debugging): print("addToDeque: %s" % node.state)
        if (self.searchType == DFS):
            dq.appendleft(node)
        elif (self.searchType == BFS):
            dq.append(node)
        else:
            raise Exception("Unknown search type %s" %self.searchType)

    # For dealing with open and closed lists for cost-based search methods
    def addToClosed(self, node, closedlist):
        if (self.debugging): print("addToClosed %d: %s" %(node.index, node.state))
        closedlist.add(node.state)

    def isClosed(self, state, closedlist):
        return state in closedlist

    def getFromOpen(self, openlist):
        c, idx, node = heappop(openlist)
        return (node if not node.removed else self.getFromOpen(openlist))

    def adjustOpenList(self, node, cost, openlist):
        """
        The node's state is already on the open list
        If the node on the open list is worse, remove it, otherwise
        ignore this node
        """
        for opencost, idx, opennode in openlist:
            if (opennode.state == node.state):
                if (cost >= opencost):
                    if (self.debugging): print("Skipping %d: %s (%d, %d vs %d, %d)"
                                      % (node.index, node.state, node.g, node.h, opennode.g, opennode.h))
                    return  # Better node already on open list
                else:
                    if (self.debugging): print("Adding %d; Marking %d: %s as removed (%d, %d vs %d, %d)"
                                      % (node.index, opennode.index, node.state, node.g, node.h, opennode.g, opennode.h))
                    opennode.removed = True  # Mark node as ignorable
                    return heappush(openlist, (cost, node.index, node))

    def addToOpen(self, node, actionCost, openlist, expanded):
        node.g = (node.parent.g if node.parent else 0) + actionCost
        if (self.searchType in (GREEDY, ASTAR)):
            node.h = node.state.costToGoal()
        cost = (node.g if self.searchType == UCS else
                node.h if self.searchType == GREEDY else node.g + node.h)
        if (node.state in expanded):  # State already in openlist
            self.adjustOpenList(node, cost, openlist)
        else:
            heappush(openlist, (cost, node.index, node))
            if (self.debugging): print("addToOpen %d: %s %d, %d" % (node.index, node.state, node.g, node.h))
            expanded.add(node.state)

    def uAddActions(self, node, dq, expanded):
        for action in self.actions:
            nextState, _ = node.state.act(action)
            if (nextState and not nextState in expanded):
                nextNode = node.addChild(nextState, action)
                self.addToDeque(nextNode, dq, expanded)

    def cAddActions(self, node, openlist, closedlist, expanded):
        for action in self.actions:
            nextState, actionCost = node.state.act(action)
            if (nextState and not self.isClosed(nextState, closedlist)):
                nextNode = node.addChild(nextState, action)
                self.addToOpen(nextNode, actionCost, openlist, expanded)

    def doSearch(self, startState):
        if (not self.searchType in SearchTypes):
            raise Exception("Unknown search type %s" %self.searchType)

        nodeCount = 0
        expanded = set()
        startNode = Node(startState)
        usearch = self.searchType in USearchTypes
        if (usearch):
            dq = deque()
            self.addToDeque(startNode, dq, expanded)
        else:
            openlist = []
            closedlist = set()
            self.addToOpen(startNode, 0, openlist, expanded)

        while len(dq if usearch else openlist) > 0:
            node = (dq.popleft() if usearch else self.getFromOpen(openlist))
            if (not usearch): self.addToClosed(node, closedlist)
            nodeCount += 1
            if (node.state.isGoal()):
                return (self.generatePath(node), nodeCount, node.g)
            elif (usearch):
                self.uAddActions(node, dq, expanded)
            else:
                self.cAddActions(node, openlist, closedlist, expanded)
        return (None, nodeCount, 0)
