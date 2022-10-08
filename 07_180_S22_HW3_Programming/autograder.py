import pickle
import argparse
import map
import readMap
from params import *
import SAR_MDP
import MDP
import SAR
from map import Locn
import simulate

mapNames = ["maps/simple.map", "maps/simple_v2.map", "maps/medium.map",
            "maps/medium_v2.map", "maps/medium_v4.map"]
default_discount = 0.95

def is_prob_distribution(distr):
    return (min(p for _,p in distr) >= 0 and max(p for _,p in distr) <= 1 and
            abs(sum(p for _,p in distr) - 1) <= 1e-5)

def same_prob_distribution(distr1, distr2):
    for s1, v1 in distr1:
        for s2, v2 in distr2:
            if (s1 == s2 and abs(v1 - v2) > 1e-5): return False
    return True

class TestHW3():
    def __init__(self, goalType=None, mapName=None):
        self.goalTypes = [goalType] if goalType else GoalTypes
        self.mapNames = [mapName] if mapName else mapNames
        self.num = self.correct = self.total_num = self.total_correct = 0

    def begin_generation(self, description):
        print("Generating refsol for %s" %description)
        self.tests = {}
        self.file_name = "autograder_files/" + description.replace(' ', '_') + ".pk"

    def end_generation(self):
        with open(self.file_name, "wb") as pkf:
            pickle.dump(self.tests, pkf)

    def begin_test(self, problem, step, description):
        print("Testing Problem %d, step %d (%s)" % (problem, step, description))
        file_name = "autograder_files/" + description.replace(' ', '_') + ".pk"
        with open(file_name, "rb") as pkf:
            self.tests = pickle.load(pkf)
        self.problem = problem; self.step = step

    def end_test(self):
        print("Score for Problem %d, step %d : %d out of %d\n"
              % (self.problem, self.step, self.correct, self.num))
        self.total_num += self.num; self.total_correct += self.correct

    def doit(self, problem, step=1):
        fn = (getattr(type(self), "%s_p%d_s%d" %('generate' if generating else 'test',
                                                 problem, step)))
        self.num = self.correct = 0
        fn(self)

    ##########  END OF UTILITY FUNCTIONS ##########

    def generate_p1_s1(self): # Sink
        self.begin_generation("sink states")
        for goalType in self.goalTypes:
            print("  Generating sink state for %s goal" %goalType)
            map = readMap.read(mapNames[0 if goalType == VISIT_GOAL else -1])
            mdp = SAR_MDP.SAR_MDP(map, goalType)
            self.tests[goalType] = mdp.create_sink_state(map, goalType)
        self.end_generation()

    def test_p1_s1(self): # Sink
        self.begin_test(1, 1, "sink states")
        for goalType in self.goalTypes:
            self.num += 1
            ref_sink = self.tests[goalType]
            mdp = SAR_MDP.SAR_MDP(ref_sink.map, goalType)
            stu_sink = mdp.create_sink_state(ref_sink.map, goalType)
            if (ref_sink == stu_sink):
                print("  Correct sink state for %s goal" %goalType)
                self.correct += 1
            else:
                print("  Incorrect sink state for %s goal" %goalType)
                print("    Refsol: %s" %ref_sink)
                print("    Yours: %s" % stu_sink)
        self.end_test()

    def generate_p1_s2(self): # States
        self.begin_generation("states")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                print("  Generating states for %s goal and %s" %(goalType, mapName))
                map = readMap.read(mapName)
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                self.tests[(goalType, mapName)] = (map, set(mdp.states))
        self.end_generation()

    def test_p1_s2(self): # States
        self.begin_test(1, 2, "states")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                self.num += 1
                map, ref_states = self.tests[(goalType, mapName)]
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                stu_states = mdp.generate_states(map, goalType)
                stu_states = (set(stu_states) if len(stu_states) > 0 else set())
                if (ref_states == stu_states):
                    print("  Correct states for %s goal and %s" %(goalType, mapName))
                    self.correct += 1
                else:
                    extras = stu_states - ref_states
                    missing = ref_states - stu_states
                    if (len(extras) > 0):
                        print("  WARNING: Found extra states for %s goal and %s:" %(goalType, mapName))
                        for extra in extras: print("    ", extra)
                        self.correct += 1
                    if (len(missing) > 0):
                        print("  ERROR: Missing states for %s goal and %s:" %(goalType, mapName))
                        for miss in missing: print("    ", miss)
        self.end_test()

    def generate_p1_s3(self): # Rewards
        self.begin_generation("rewards")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                print("  Generating rewards for %s goal and %s" %(goalType, mapName))
                map = readMap.read(mapName)
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                self.tests[(goalType, mapName)] = (map, set(mdp.states), mdp.rewards)
        self.end_generation()

    def test_p1_s3(self): # Rewards
        self.begin_test(1, 3, "rewards")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                self.num += 1
                map, ref_states, ref_rewards = self.tests[(goalType, mapName)]
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                stu_rewards = mdp.generate_rewards(mdp.states)
                stu_states = set(mdp.states)
                extras = stu_states - ref_states
                missing = ref_states - stu_states
                if (len(extras) > 0): print("  Ignoring the %d extra states in your solution" %len(extras))
                all_correct = True
                for state in ref_states:
                    ref_reward = ref_rewards[state]
                    stu_reward = stu_rewards.get(state)
                    if (stu_reward == None):
                        if all_correct: print(" ERROR for %s goal and %s" %(goalType, mapName))
                        print("  Your solution is missing reward for %s" %state)
                        all_correct = False
                    elif (abs(ref_reward - stu_reward) > 1e-5):
                        if all_correct: print(" ERROR for %s goal and %s" %(goalType, mapName))
                        print("  Incorrect reward for %s: ref: %s; yours: %s" %(state, ref_reward, stu_reward))
                        all_correct = False
                if (len(missing) > 0):
                    print("  Your solution is missing %d states -- make sure you pass problem 1, step 1" % len(missing))
                if all_correct:
                    print("  Rewards correct for %s goal and %s" %(goalType, mapName))
                    self.correct += 1
        self.end_test()

    def generate_p2_s1(self): # Transitions
        self.begin_generation("transitions")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                print("  Generating transitions for %s goal and %s" % (goalType, mapName))
                map = readMap.read(mapName)
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                self.tests[(goalType, mapName)] = (map, set(mdp.states), mdp.transitions)
        self.end_generation()

    def test_p2_s1(self): # Transitions
        self.begin_test(2, 1, "transitions")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                self.num += 1
                map, ref_states, ref_transitions = self.tests[(goalType, mapName)]
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                stu_transitions = mdp.generate_transitions(mdp.states, mdp.actions)
                stu_states = set(mdp.states)
                extras = stu_states - ref_states
                missing = ref_states - stu_states
                if (len(extras) > 0): print("  Ignoring the %d extra states in your solution" %len(extras))
                all_correct = True
                for state_action in ref_transitions:
                    state, action = state_action
                    ref_trans = ref_transitions[state_action]
                    stu_trans = stu_transitions.get(state_action)
                    if (stu_trans == None):
                        if all_correct: print(" ERROR for %s goal and %s" %(goalType, mapName))
                        print("  Your solution is missing transition for %s" %state)
                        all_correct = False
                    elif not is_prob_distribution(stu_trans):
                        if all_correct: print(" ERROR for %s goal and %s" %(goalType, mapName))
                        print("  Transition not a legal probability distribution for %s: %s" % (state, stu_trans))
                        all_correct = False
                    elif not same_prob_distribution(ref_trans, stu_trans):
                        if all_correct: print(" ERROR for %s goal and %s" %(goalType, mapName))
                        print("  Incorrect transitions for %s: ref: %s; yours: %s" %(state, ref_trans, stu_trans))
                        all_correct = False
                if (len(missing) > 0):
                    print("  Your solution is missing %d states -- make sure you pass problem 1, step 1" % len(missing))
                if all_correct:
                    print("  Rewards correct for %s goal and %s" %(goalType, mapName))
                    self.correct += 1
        self.end_test()

    def generate_p3_s1(self): # Expected
        self.begin_generation("expected values")
        state_list = ["Land of Mages", "Princess Without Subjects", "Royal Celesteria",
                      "Land of Truth Tellers", "Rostoff", "Qunorts"]
        actions = ["Travel", "Fight", "Existential Crisis"]
        rewards = { "Land of Mages": 10,
                    "Princess Without Subjects": -50,
                    "Royal Celesteria": 30,
                    "Land of Truth Tellers": 10,
                    "Rostoff": -100000,
                    "Qunorts": 50
                    }
        transitions = {
                ("Land of Mages", "Travel"): [("Princess Without Subjects", 0.5), ("Royal Celesteria", 0.5)],
                ("Princess Without Subjects", "Travel"): [("Royal Celesteria", 1.0)],
                ("Princess Without Subjects", "Fight"): [("Royal Celesteria", 0.5), ("Princess Without Subjects", 0.5)],
                ("Princess Without Subjects", "Existential Crisis"): [("Princess Without Subjects", 1.0)],
                ("Royal Celesteria", "Travel"): [("Land of Truth Tellers", 1.0)],
                ("Land of Truth Tellers", "Travel"): [("Rostoff", 0.8), ("Qunorts", 0.2)],
                ("Rostoff", "Existential Crisis"): [("Rostoff", 1.0)],
                ("Qunorts", "Travel"): [("Royal Celesteria", 0.3), ("Rostoff", 0.7)]
            }
        values = { "Land of Mages": 5,
                    "Princess Without Subjects": -10,
                    "Royal Celesteria": 0,
                    "Land of Truth Tellers": -5,
                    "Rostoff": 10,
                    "Qunorts": -10
            }
        self.tests['mdp'] = [state_list, actions, transitions, rewards, values]
        for state in state_list:
            for action in actions:
                self.tests[(state, action)] = MDP.expected_value(state, action, transitions, values)
        self.end_generation()

    def test_p3_s1(self): # Expected
        self.begin_test(3, 1, "expected values")
        state_list, actions, transitions, _, values = self.tests['mdp']
        for state in state_list:
            for action in actions:
                self.num += 1
                ref_expected = self.tests[(state, action)]
                try:
                    stu_expected = MDP.expected_value(state, action, transitions, values)
                    if (abs(stu_expected - ref_expected) > 1e-5):
                        print("  Incorrect value for state '%s' and action '%s': ref: %s; yours: %s"
                              %(state, action, ref_expected, stu_expected))
                    else:
                        print("  Correct expected value for tate '%s' and action '%s' (%s)" %(state, action, ref_expected))
                        self.correct += 1
                except Exception as err:
                    print("  Expected value function failed for state '%s' and action '%s': (%s)"  %(state, action, err))
        self.end_test()

    def generate_p3_s2(self): # Bellman
        self.begin_generation("Bellman update")
        with open("autograder_files/expected_values.pk", "rb") as pkf:
            state_list, actions, transitions, rewards, values = pickle.load(pkf)['mdp']
        self.tests['mdp'] = [state_list, actions, transitions, rewards, values]
        for state in state_list:
            for action in actions:
                self.tests[(state, action)] = MDP.bellman_update(state, actions, transitions, rewards,
                                                                 values, default_discount)
        self.end_generation()

    def test_p3_s2(self): # Bellman
        self.begin_test(3, 2, "Bellman update")
        state_list, actions, transitions, rewards, values = self.tests['mdp']
        for state in state_list:
            for action in actions:
                self.num += 1
                ref_update = self.tests[(state, action)]
                try:
                    stu_update = MDP.bellman_update(state, actions, transitions, rewards,
                                                    values, default_discount)
                    if (abs(stu_update - ref_update) > 1e-5):
                        print("  Incorrect update for state '%s' and action '%s': ref: %s; yours: %s"
                              % (state, action, ref_update, stu_update))
                    else:
                        print("  Correct Bellman update for tate '%s' and action '%s' (%s)" % (state, action, ref_update))
                        self.correct += 1
                except Exception as err:
                    print("  Bellman update function failed for state '%s' and action '%s': (%s)" % (state, action, err))
        self.end_test()

    def generate_p4_s1(self): # Update
        self.begin_generation("update state")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                print("  Generating update state tests for %s goal and %s" % (goalType, mapName))
                map = readMap.read(mapName)
                mdp = SAR_MDP.SAR_MDP(map, goalType)
                updates = {}
                for state_action in mdp.transitions:
                    trans = mdp.transitions[state_action]
                    for next_state, _ in trans:
                        updates[state_action] = next_state
                self.tests[(goalType, mapName)] = (map, updates)
        self.end_generation()

    def test_p4_s1(self): # Update
        self.begin_test(4, 1, "update state")
        exec = SAR_MDP.SAR_Executor(None, None)
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                self.num += 1
                all_correct = True
                map, updates = self.tests[(goalType, mapName)]
                for state_action in updates:
                    state, action = state_action
                    ref_next_state = updates[state_action]
                    exec.state = state
                    exec.update_state(action, ref_next_state.locn)
                    stu_next_state = exec.state
                    if (ref_next_state != stu_next_state):
                        if all_correct: print(" ERROR for %s goal and %s" %(goalType, mapName))
                        print("  Incorrect update for %s and action %s" %state_action)
                        print("    Refsol: %s" % ref_next_state)
                        print("    Yours: %s" % stu_next_state)
                        all_correct = False
                if all_correct:
                    print("  Update state correct for %s goal and %s" %(goalType, mapName))
                    self.correct += 1
        self.end_test()

    def generate_p4_s2(self): # Choice
        self.begin_generation("action choice")
        with open("autograder_files/expected_values.pk", "rb") as pkf:
            state_list, actions, transitions, rewards, values = pickle.load(pkf)['mdp']
        mdp = MDP.MDP(state_list, actions, transitions, rewards, default_discount)
        policy = mdp.policy_iteration()
        exec = SAR_MDP.SAR_Executor(None, policy)
        self.tests['exec'] = (state_list, policy)
        for state in state_list:
            exec.state = state
            self.tests[state] = exec.choose_action()
        self.end_generation()

    def test_p4_s2(self): # Choice
        self.begin_test(4, 2, "action choice")
        state_list, policy = self.tests['exec']
        exec = SAR_MDP.SAR_Executor(None, policy)
        for state in state_list:
            self.num += 1
            ref_action = self.tests[state]
            try:
                exec.state = state
                stu_action = exec.choose_action()
                if (ref_action != stu_action):
                    print("  Incorrect action choice for state '%s': ref: %s; yours: %s" %(state, ref_action, stu_action))
                else:
                    print("  Correct action choice for state '%s': (%s)" % (state, ref_action))
                    self.correct += 1
            except Exception as err:
                print("  Action choice function failed for state '%s': (%s)" % (state, err))
        self.end_test()

class TestIntegration(TestHW3):
    def __init__(self, goalType, map, useGraphics, maxSteps, simSpeed=0.1, discount=default_discount):
        super().__init__(goalType, map)
        self.useGraphics = useGraphics
        self.maxSteps = maxSteps
        self.simSpeed = simSpeed
        self.discount = discount

    def test_p1_s1(self):
        print("Testing complete integration:")
        for goalType in self.goalTypes:
            for mapName in self.mapNames:
                print("  Testing with %s and %s goal" %(mapName, goalType))
                self.simulate_policy(mapName, goalType)

    def simulate_policy(self, mapName, goalType):
        map = readMap.read(mapName)
        mdp = SAR_MDP.SAR_MDP(map, goalType, discount = self.discount)
        #policy = mdp.policy_iteration(max_iters=10000)
        policy = mdp.value_iteration(max_iters=10000)
        exec = SAR_MDP.SAR_Executor(SAR.createStartState(map, goalType), policy)
        simr = simulate.Simulator(map, goalType, self.useGraphics, title="S&R: MDP", speed=self.simSpeed,
                                  probabilistic=True)
        cost = simr.doPolicy(exec, self.maxSteps)
        if cost:
            print("Simulation reward: %s" % -cost)
        else:
            print("POLICY FAILED TO ACHIEVE %s GOALS AFTER %d STEPS" % (goalType, self.maxSteps))

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--problem')
parser.add_argument('-s', '--step')
parser.add_argument('-g', '--goal', nargs='?')
parser.add_argument('-m', '--map', nargs='?')
parser.add_argument('-t', '--test', action='store_true')
parser.add_argument('--no-graphics', action='store_true')
parser.add_argument('--debugging', action='store_true')
parser.add_argument('--generate', action='store_true')
parser.add_argument('--max-steps', nargs='?', default=1000)
parser.add_argument('--discount', nargs='?', default=1)

args = parser.parse_args()
generating = args.generate

if args.debugging:
    SAR.debugging = True
    SAR_MDP.debugging = True

if args.goal and not args.goal in GoalTypes:
    raise Exception("%s unknown goal; options are: %s" %(args.goal, ', '.join(GoalTypes)))

if (args.test):
    integrationTest = TestIntegration(args.goal, args.map, not args.no_graphics,
                                      maxSteps=int(args.max_steps), discount=float(args.discount))
    integrationTest.doit(1)
else:
    testHW3 = TestHW3(args.goal, args.map)
    if (args.problem == None or args.problem == "1"):
        if (args.step == None or args.step == "1"): testHW3.doit(1, 1)
        if (args.step == None or args.step == "2"): testHW3.doit(1, 2)
        if (args.step == None or args.step == "3"): testHW3.doit(1, 3)
    if (args.problem == None or args.problem == "2"): testHW3.doit(2)
    if (args.problem == None or args.problem == "3"):
        if (args.step == None or args.step == "1"): testHW3.doit(3, 1)
        if (args.step == None or args.step == "2"): testHW3.doit(3, 2)
    if (args.problem == None or args.problem == "4"):
        if (args.step == None or args.step == "1"): testHW3.doit(4, 1)
        if (args.step == None or args.step == "2"): testHW3.doit(4, 2)

    if not generating:
        print("Total Correct: %d out of %d" %(testHW3.total_correct, testHW3.total_num))
