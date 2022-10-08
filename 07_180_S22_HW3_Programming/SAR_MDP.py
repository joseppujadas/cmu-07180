import math
import typing
import SAR
import MDP
from params import *
from map import *

DONE = 'DONE'

GOAL_REWARD = 500

debugging = False

class SAR_MDP(MDP.MDP):

    def __init__(self, map, goalType, discount=0.95):
        states = self.generate_states(map, goalType)
        actions = [DONE, NORTH, SOUTH, EAST, WEST]
        if goalType == RETRIEVE_GOAL:
            actions += [PICKUP, PUTDOWN]
        rewards = self.generate_rewards(states)
        transitions = self.generate_transitions(states, actions)
        super().__init__(states, actions, transitions, rewards, discount)

    """
    Create the sink state. Recall that the location should be at (-1, -1) and
    the status should indicate that the goal has been achieved (either the VISITED or the RETRIEVED)

    :params
    map: the search and rescue map
    goalType: one of VISIT_GOAL or RETRIEVE_GOAL

    :return
    sink_state: the sink state as defined in the write up
    """
    def create_sink_state(self, map: Map, goalType):
        # BEGIN STUDENT CODE FOR PROBLEM 1
        # END STUDENT CODE FOR PROBLEM 1
        if goalType == RETRIEVE_GOAL:
            return SAR.SAR_State(map, Locn(-1,-1), RETRIEVED, map.getVictims(), goalType)
        else:
            return SAR.SAR_State(map, Locn(-1,-1), VISITED, map.getVictims(), goalType)

    """
    Generate the list of all feasible states. While non feasible states will not be penalized, note that generating
    too many states may slow down your code and the autograder. Furthermore, it may make debugging more difficult.

    :params
    the_map: the search and rescue map
    goalType: one of VISIT_GOAL or RETRIEVE_GOAL

    :return
    states: a list of all feasible states
    """
    def generate_states(self, map, goalType):
        sink_state = self.create_sink_state(map, goalType)
        states = ([sink_state] if sink_state else [])
        # BEGIN STUDENT CODE FOR PROBLEM 1
        for row in map.grid:
            for cell in row:
                if not cell.isWall():
                    if cell.locn not in map.getVictims():
                        states.append(SAR.SAR_State(map,cell.locn,SEARCHING,map.getVictims(),goalType))
                    else:
                        states.append(SAR.SAR_State(map,cell.locn,VISITED,map.getVictims(),goalType))
                    if goalType == RETRIEVE_GOAL:
                        states.append(SAR.SAR_State(map,cell.locn,CARRYING,map.getVictims(),goalType))
                        if cell.isEntry():
                            states.append(SAR.SAR_State(map,cell.locn,RETRIEVED,map.getVictims(),goalType))



        # END STUDENT CODE FOR PROBLEM 1

        if debugging:
            print("Generate states:")
            for state in states: print(" ", state)
            print("# States: %d\n" %len(states))
        return states

    """
    Generate the dictionary mapping states to their rewards (where costs are negative rewards)
    Feel free to reuse moveActionCost in SAR.py

    :param
    state_list: the list containing all feasible states

    :return
    rewards: the dictionary mapping states to their rewards
    """
    def generate_rewards(self, state_list):
        rewards = {}
        # BEGIN STUDENT CODE FOR PROBLEM 1
        for state in state_list:
            if state == self.create_sink_state(state.map,state.goalType):
                rewards[state] = 0
            elif state.status == RETRIEVED and state.goalType == RETRIEVE_GOAL:
                rewards[state] = 500
            elif state.status == VISITED and state.goalType == VISIT_GOAL:
                rewards[state] = 500
            else:
                rewards[state] = -state.moveActionCost()
        # END STUDENT CODE FOR PROBLEM 1

        if debugging:
            print("Generate rewards:")
            for reward in rewards: print(" ", reward, rewards[reward])
            print("# Rewards: %d\n" %len(rewards))
        return rewards

    """
    Generate the transitions dictionary. Recall that each key is a (state, action) tuple and the value is an array
    of (state, probability) pairs, where "state" is of type SAR_State.

    For instance, {
                    (<State [1,2]...>, NORTH): [(<State [2,2]...>, 0.6), (<State [1,2]...>, 0.4)],
                    (<State [2,2]...>, SOUTH): [(<State [1,2]...>, 1.0)]
                  }
    See the write up for the actual transition model that needs to be implemented

    Note: you are free to use functions from HW2 in SAR.py to help compute the transitions
    Note: you do not need a transition for every (state, probability) pair, only those with non-zero transition probability
    Note: if in a goal state, all actions should lead to the sink state
    Note: for the RETRIEVE_GOAL, moving (N, S, E, W) from a victim location with VISITED status should not be feasible

    :param
    state_list: the list containing all feasible states
    actions: the list of all actions

    :return
    transitions: the dictionary mapping (state, action) tuples to their corresponding list of (state, probability) pairs
    """

    def generate_transitions(self, state_list, actions):
        transitions = {}
        # BEGIN STUDENT CODE FOR PROBLEM 2
        for state in state_list:
            for action in actions:
                stateProbs = []
                sink = self.create_sink_state(state.map,state.goalType)
                isGoal = (state.status == RETRIEVED and state.goalType == RETRIEVE_GOAL) or (state.status == VISITED and state.goalType == VISIT_GOAL)
                if (isGoal and action == DONE) or state == sink:
                    stateProbs.append((sink,1.0))
                    transitions[(state,action)] = stateProbs
                if state != sink and action != DONE:
                    cost = math.sqrt(state.moveActionCost())
                    pLR = 0.05 * cost
                    pStay = 0.01 * cost
                    pF = 1 - 2*pLR - pStay
                    if(action == NORTH):
                        if(state.map.canMove(WEST,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(WEST)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(EAST,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(EAST)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(NORTH,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(NORTH)[0],pF))
                        else:
                            pStay += pF
                        stateProbs.append((state,pStay))
                    elif(action == SOUTH):
                        if(state.map.canMove(WEST,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(WEST)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(EAST,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(EAST)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(SOUTH,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(SOUTH)[0],pF))
                        else:
                            pStay += pF
                        stateProbs.append((state,pStay))
                    elif(action == EAST):
                        if(state.map.canMove(SOUTH,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(SOUTH)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(EAST,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(EAST)[0],pF))
                        else:
                            pStay += pF

                        if(state.map.canMove(NORTH,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(NORTH)[0],pLR))
                        else:
                            pStay += pLR
                        stateProbs.append((state,pStay))
                    elif(action == WEST):
                        if(state.map.canMove(NORTH,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(NORTH)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(SOUTH,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(SOUTH)[0],pLR))
                        else:
                            pStay += pLR

                        if(state.map.canMove(WEST,state.locn.row,state.locn.col)):
                            stateProbs.append((state.tryToMove(WEST)[0],pF))
                        else:
                            pStay += pF
                        stateProbs.append((state,pStay))
                    elif(action == PUTDOWN):
                        stateProbs.append((state,1.0))
                    elif(action == PICKUP):
                        stateProbs.append((state,1.0))
                    if len(stateProbs) != 0:
                        transitions[(state,action)] = stateProbs

        # END STUDENT CODE FOR PROBLEM 2

        if debugging:
            for trans in transitions:
                print("Generate states:")
                print(" ", trans, transitions[trans])
                if (abs(sum(p for _, p in transitions[trans]) - 1.0) > 1e-10 or
                    min(p for _, p in transitions[trans]) < 0.0 or
                    max(p for _, p in transitions[trans]) > 1.0):
                    raise Exception("   NOT PROBABILITY DISTRIBUTION: %s %s" %(transitions[trans], sum(p for _, p in transitions[trans])))
            print("# Transitions: %d\n" %len(transitions))
        return transitions

"""
Class to execute a search-and-rescue policy
"""
class SAR_Executor:

    def __init__(self, start_state, policy):
        self.policy = policy
        self.state = start_state

    """
    Update self.state (which is of type SAR_State) to indicate the result of the action.
    Note: This function should be very similar to the "act" function in SAR_State - feel free
        to adapt as much of the sub-functions that it calls as you want

    :param
    action: the last action that was taken
    new_locn: the new location that resulted from the action (which may be the same as self.state.locn)
    """
    def update_state(self, action, new_locn):
        # BEGIN STUDENT CODE FOR PROBLEM 3
        newStatus = self.state.status
        isVictim = new_locn in self.state.map.getVictims()
        isEntry = new_locn == self.state.map.getCellL(self.state.locn).isEntry()
        if self.state.status == SEARCHING and isVictim:
            newStatus = VISITED
        elif self.state.status == CARRYING and action == PUTDOWN:
            newStatus = RETRIEVED
        elif action == PICKUP and isVictim:
            newStatus = CARRYING
        self.state = SAR.SAR_State(self.state.map,new_locn,newStatus,self.state.victims,self.state.goalType)


        # END STUDENT CODE FOR PROBLEM 3


    """
    Use self.policy to return the optimal action for self.state
    """
    def choose_action(self) -> object:
        # BEGIN STUDENT CODE FOR PROBLEM 3
        return self.policy[self.state]
        # END STUDENT CODE FOR PROBLEM 3
