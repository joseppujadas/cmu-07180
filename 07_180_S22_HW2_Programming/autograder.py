generating = False # If True, then generate answers to tests
testing_refsol = False # If True, then test against the refsol

import copy
import readMap
import map
from params import *
import argparse
if generating or testing_refsol:
    import sys
    sys.path.insert(0, '..')
    import refsol.SAR as SAR
    import search
else:
    import SAR

class TestTransitions():
    num = 0
    correct = 0
    total_num = 0
    total_correct = 0

    def check_transition(self, start, action, ref):
        if (generating): return self.generate_transition(start, action)
        self.num += 1
        # Apparently, a deep-copied map is not equal to the original
        s0 = SAR.SAR_State(start.map, copy.copy(start.locn), start.status,
                            copy.copy(start.victims), start.goalType)
        stu = s0.act(action)
        if (start != s0):
            print("  Current state was altered %s vs %s" %(start, s0))
        elif (ref == stu):
            print("  Correct transition for action %s from %s:" % (action, start))
            self.correct += 1
            return True
        else:
            if (ref[0] != stu[0]):
                print("  Incorrect transition for action %s from %s:" % (action, start))
                print("    Refsol: %s" % ref[0])
                print("    Yours: %s" % stu[0])
            else:
                print("  Incorrect cost for transitioning to %s:" %ref[0])
                print("    Refsol: %s" % ref[1])
                print("    Yours: %s" % stu[1])
            return False

    def generate_transition(self, start, action): # Generate the test case answer
        next, cost = start.act(action)
        action_name = ('EAST' if action == EAST else 'WEST' if action == WEST else
                       'NORTH' if action == NORTH else 'SOUTH' if action == SOUTH else
                       'PICKUP' if action == PICKUP else 'PUTDOWN')
        print("  Transition of %s from %s:" % (action_name, start))
        if (next == None): # Invalid move
            print("    self.check_transition(s0, %s, (None, 0))" %action_name)
        else:
            print("    s_ref = SAR.SAR_State(m, map.Locn(%d,%d), %s, victims, %s)"
                  %(next.locn.row, next.locn.col,
                    ('SEARCHING' if next.status == SEARCHING else
                    'VISITED' if next.status == VISITED else
                    'CARRYING' if next.status == CARRYING else 'RETRIEVED'),
                    ('VISIT_GOAL' if next.goalType == VISIT_GOAL else 'RETRIEVE_GOAL')))
            print("    self.check_transition(s0, %s, (s_ref, %d))" %(action_name, cost))

    def test_p1(self):
        print("Testing Problem 1 transitions")
        self.correct = 0; self.num = 0
        m = readMap.read("maps/simple.map")
        victims = m.getVictims()

        s0 = SAR.SAR_State(m, map.Locn(4,4), SEARCHING, victims, VISIT_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(3,4), SEARCHING, victims, VISIT_GOAL)
        self.check_transition(s0, NORTH, (s_ref, 2))
        s_ref = SAR.SAR_State(m, map.Locn(4,5), SEARCHING, victims, VISIT_GOAL)
        self.check_transition(s0, EAST, (s_ref, 1))
        self.check_transition(s0, WEST, (None, 0))

        s0 = SAR.SAR_State(m, map.Locn(2,5), SEARCHING, victims, VISIT_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2,6), SEARCHING, victims, VISIT_GOAL)
        self.check_transition(s0, EAST, (s_ref, 3))
        s_ref = SAR.SAR_State(m, map.Locn(3,5), SEARCHING, victims, VISIT_GOAL)
        self.check_transition(s0, SOUTH, (s_ref, 1))
        self.check_transition(s0, WEST, (None, 0))

        s0 = SAR.SAR_State(m, map.Locn(1,3), SEARCHING, victims, VISIT_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(1,2), VISITED, victims, VISIT_GOAL)
        self.check_transition(s0, WEST, (s_ref, 1))
        s0 = s_ref
        s_ref = SAR.SAR_State(m, map.Locn(1,3), VISITED, victims, VISIT_GOAL)
        self.check_transition(s0, EAST, (s_ref, 1))
        s0 = s_ref
        s_ref = SAR.SAR_State(m, map.Locn(1, 4), VISITED, victims, VISIT_GOAL)
        self.check_transition(s0, EAST, (s_ref, 1))

        print("Score for Problem 1 transitions: %d out of %d\n" %(self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct

    def test_p2(self):
        print("Testing Problem 2 transitions")
        self.correct = 0;
        self.num = 0
        m = readMap.read("maps/simple.map")
        victims = m.getVictims()

        s0 = SAR.SAR_State(m, map.Locn(1,2), VISITED, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(1,2), CARRYING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PICKUP, (s_ref, PICKUP_COST))
        s0.status = CARRYING
        self.check_transition(s0, PICKUP, (None, 0))
        s0.status = SEARCHING
        self.check_transition(s0, PICKUP, (s_ref, PICKUP_COST))

        s0 = SAR.SAR_State(m, map.Locn(1,3), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PICKUP, (None, 0))
        s0.status = VISITED
        self.check_transition(s0, PICKUP, (None, 0))
        s0.status = CARRYING
        self.check_transition(s0, PICKUP, (None, 0))

        s0 = SAR.SAR_State(m, map.Locn(4,4), CARRYING, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(4,4), RETRIEVED, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PUTDOWN, (s_ref, PUTDOWN_COST))
        s0.status = VISITED
        self.check_transition(s0, PUTDOWN, (None, 0))
        s0.status = SEARCHING
        self.check_transition(s0, PUTDOWN, (None, 0))

        s0 = SAR.SAR_State(m, map.Locn(1,3), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PICKUP, (None, 0))
        s0.status = VISITED
        self.check_transition(s0, PICKUP, (None, 0))
        s0.status = CARRYING
        self.check_transition(s0, PICKUP, (None, 0))

        s0 = SAR.SAR_State(m, map.Locn(3, 4), CARRYING, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(4, 4), CARRYING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, SOUTH, (s_ref, 1))
        s0 = SAR.SAR_State(m, map.Locn(3, 4), VISITED, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(4, 4), VISITED, victims, RETRIEVE_GOAL)
        self.check_transition(s0, SOUTH, (s_ref, 1))

        s0 = SAR.SAR_State(m, map.Locn(2, 5), CARRYING, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2, 6), CARRYING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, EAST, (s_ref, 9))
        s0 = SAR.SAR_State(m, map.Locn(2, 6), CARRYING, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2, 5), CARRYING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, WEST, (s_ref, 4))
        s0 = SAR.SAR_State(m, map.Locn(2, 5), VISITED, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2, 6), VISITED, victims, RETRIEVE_GOAL)
        self.check_transition(s0, EAST, (s_ref, 3))

        print("Score for Problem 2 transitions: %d out of %d\n" %(self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct

    def test_p3(self):
        print("Testing Problem 3 transitions")
        self.correct = 0;
        self.num = 0
        m = readMap.read("maps/medium_v4.map")
        victims = m.getVictims()

        s0 = SAR.SAR_State(m, map.Locn(2, 6), SEARCHING, victims, VISIT_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2, 5), VISITED, victims, VISIT_GOAL)
        self.check_transition(s0, WEST, (s_ref, 1))
        s0 = SAR.SAR_State(m, map.Locn(10, 26), SEARCHING, victims, VISIT_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(11, 26), VISITED, victims, VISIT_GOAL)
        self.check_transition(s0, SOUTH, (s_ref, 1))
        s0 = s_ref
        s_ref = SAR.SAR_State(m, map.Locn(11, 25), VISITED, victims, VISIT_GOAL)
        self.check_transition(s0, WEST, (s_ref, 1))

        s0 = SAR.SAR_State(m, map.Locn(2,5), VISITED, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2,5), CARRYING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PICKUP, (s_ref, PICKUP_COST))
        s0 = SAR.SAR_State(m, map.Locn(2,17), VISITED, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(2,17), CARRYING, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PICKUP, (s_ref, PICKUP_COST))

        s0 = SAR.SAR_State(m, map.Locn(16,6), CARRYING, victims, RETRIEVE_GOAL)
        s_ref = SAR.SAR_State(m, map.Locn(16,6), RETRIEVED, victims, RETRIEVE_GOAL)
        self.check_transition(s0, PUTDOWN, (s_ref, PUTDOWN_COST))

        print("Score for Problem 3 transitions: %d out of %d\n" % (self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct


import search
class TestHeuristics():
    num = 0
    correct = 0
    total_num = 0
    total_correct = 0
    def check_heuristic(self, state, ref_est, true_cost):
        if (generating): return self.generate_heuristic(state)
        self.num += 1
        stu_est = state.costToGoal()
        if (stu_est < 0):
            print("  !!Heuristic for %s is negative!! (%s)" %(state, stu_est))
            return False
        elif (stu_est > true_cost):
            print("  Heuristic for %s is not admissible:" %state)
            print("    True cost to goal: %s" % true_cost)
            print("    Yours: %s" % stu_est)
            return False
        elif (ref_est == stu_est):
            print("  Heuristic for %s matches refsol (%s):" %(state, ref_est))
            self.correct += 1
            return True
        elif (ref_est < stu_est):
            print("  Heuristic for %s matches more informed than refsol!:" %state)
            print("    Refsol: %s" % ref_est)
            print("    Yours: %s" % stu_est)
            self.correct += 1
            return True
        else:
            print("  Heuristic for %s less informed than refsol:" %state)
            print("    Refsol: %s" % ref_est)
            print("    Yours: %s" % stu_est)
            return False

    def generate_heuristic(self, state): # Generate the test case answer
        searchInstance = search.Search(search.ASTAR, Actions, False)
        _, _, true_cost = searchInstance.doSearch(state)
        print("Cost from %s to goal:" %state)
        print("     self.check_heuristic(s0, %d, %d)" %(state.costToGoal(), true_cost))

    def test_p1(self):
        print("Testing Problem 1 heuristics")
        self.correct = 0; self.num = 0
        m = readMap.read("maps/simple.map")
        victims = m.getVictims()

        s0 = SAR.SAR_State(m, map.Locn(1, 8), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 6, 6)
        s0 = SAR.SAR_State(m, map.Locn(4, 4), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 5, 8)
        s0 = SAR.SAR_State(m, map.Locn(1, 3), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 1, 1)
        s0 = SAR.SAR_State(m, map.Locn(1, 2), VISITED, victims, VISIT_GOAL)
        self.check_heuristic(s0, 0, 0)
        s0 = SAR.SAR_State(m, map.Locn(1, 3), VISITED, victims, VISIT_GOAL)
        self.check_heuristic(s0, 0, 0)

        print("Score for Problem 1 heuristics: %d out of %d\n" % (self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct

    def test_p2(self):
        print("Testing Problem 2 heuristics")
        self.correct = 0; self.num = 0
        m = readMap.read("maps/simple.map")
        victims = m.getVictims()

        s0 = SAR.SAR_State(m, map.Locn(4,4), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 20, 28)
        s0 = SAR.SAR_State(m, map.Locn(1, 2), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 15, 20)
        s0 = SAR.SAR_State(m, map.Locn(1, 3), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 16, 21)
        s0 = SAR.SAR_State(m, map.Locn(1, 2), VISITED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 15, 20)
        s0 = SAR.SAR_State(m, map.Locn(1, 3), VISITED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 16, 21)
        s0 = SAR.SAR_State(m, map.Locn(1, 2), CARRYING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 10, 15)
        s0 = SAR.SAR_State(m, map.Locn(1, 3), CARRYING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 9, 14)
        s0 = SAR.SAR_State(m, map.Locn(4, 4), CARRYING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 5, 5)
        s0 = SAR.SAR_State(m, map.Locn(4, 4), RETRIEVED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 0, 0)
        s0 = SAR.SAR_State(m, map.Locn(3, 4), RETRIEVED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 0, 0)

        print("Score for Problem 2 heuristics: %d out of %d\n" % (self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct

    def test_p3(self):
        print("Testing Problem 3 heuristics")
        self.correct = 0; self.num = 0
        m = readMap.read("maps/medium_v4.map")
        victims = m.getVictims()

        s0 = SAR.SAR_State(m, m.getEntry(), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 15, 27)
        s0 = SAR.SAR_State(m, map.Locn(16, 9), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 16, 24)
        s0 = SAR.SAR_State(m, map.Locn(16, 12), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 15, 21)
        s0 = SAR.SAR_State(m, map.Locn(16, 18), SEARCHING, victims, VISIT_GOAL)
        self.check_heuristic(s0, 13, 19)

        s0 = SAR.SAR_State(m, map.Locn(2, 5), VISITED, victims, VISIT_GOAL)
        self.check_heuristic(s0, 0, 0)
        s0 = SAR.SAR_State(m, map.Locn(11, 26), VISITED, victims, VISIT_GOAL)
        self.check_heuristic(s0, 0, 0)

        s0 = SAR.SAR_State(m, m.getEntry(), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 40, 68)
        s0 = SAR.SAR_State(m, map.Locn(16, 9), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 43, 65)
        s0 = SAR.SAR_State(m, map.Locn(16, 12), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 44, 62)
        s0 = SAR.SAR_State(m, map.Locn(16, 18), SEARCHING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 48, 64)

        s0 = SAR.SAR_State(m, map.Locn(2, 5), VISITED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 25, 45)
        s0 = SAR.SAR_State(m, map.Locn(11, 26), VISITED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 35, 45)

        s0 = SAR.SAR_State(m, map.Locn(2, 11), CARRYING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 24, 38)
        s0 = SAR.SAR_State(m, map.Locn(11, 2), CARRYING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 14, 14)
        s0 = SAR.SAR_State(m, m.getEntry(), CARRYING, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 5, 5)
        s0 = SAR.SAR_State(m, m.getEntry(), RETRIEVED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 0, 0)
        s0 = SAR.SAR_State(m, map.Locn(16, 7), RETRIEVED, victims, RETRIEVE_GOAL)
        self.check_heuristic(s0, 0, 0)

        print("Score for Problem 3 heuristics: %d out of %d\n" % (self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--problem')
parser.add_argument('-s', '--step')
args = parser.parse_args()

transitionsTest = TestTransitions()
heuristicsTest = TestHeuristics()
if (args.problem == None or args.problem == "1"):
    if (args.step == None or args.step == "1"): transitionsTest.test_p1()
    if (args.step == None or args.step == "2"): heuristicsTest.test_p1()
if (args.problem == None or args.problem == "2"):
    if (args.step == None or args.step == "1"): transitionsTest.test_p2()
    if (args.step == None or args.step == "2"): heuristicsTest.test_p2()
if (args.problem == None or args.problem == "3"):
    if (args.step == None or args.step == "1"): transitionsTest.test_p3()
    if (args.step == None or args.step == "2"): heuristicsTest.test_p3()

print("Total Correct: %d out of %d" %(transitionsTest.total_correct + heuristicsTest.total_correct,
                                      transitionsTest.total_num + heuristicsTest.total_num))
