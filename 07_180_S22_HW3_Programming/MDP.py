"""
 Code to do value and policy iteration
 Inputs:
 1) A list of states
    Note: the states can be strings, as shown below, integers, or any data structure you prefer
 2) A list of actions (strings, defined in params.py)
 3) A dictionary of transitions, where each key is a state/action tuple and
    the value is an array of state/probability pairs.
    For instance: {('S1', NORTH): [('S2', 0.6), ('S3', 0.4)],
                   ('S3', SOUTH): [('S1', 1.0)]}
    Note: you do not need a transition for every state/action pair, only those with non-zero transition probability
 4) A dictionary of rewards, where each key is a state and the value is the reward of being in that state.
    For instance: {'S1': 2, 'S2': 4, S3': -5}
    Note: costs are negative rewards
    Note: every state must have a reward specified
 5) A discount value (defaults to 0.95)
 Output: A dictionary, where each key is a state (same representation as used
    by the input), and the value is an action
"""
from typing import List, Dict

debugging = False

"""
Compute the expected value of performing an action at a specific state
(see the writeup and the Markov Models lecture for the formula to implement)

:param
state: the state that we are currently in
action: the action that we are considering
transitions: a dictionary of transitions, where the key is a (state, action) tuple and
   the value is a list of (state, probability) tuples
values: a dictionary mapping states to their current values

:return
val: the expected value of performing the given action at the current state
"""
def expected_value(state, action, transitions, values):
    # BEGIN STUDENT CODE FOR PART 3
    val = 0
    if (state,action) in transitions:
        for s,p in transitions[state,action]:
            val += (p * values[s])
    return val
    # END STUDENT CODE FOR PART 3


"""
Compute the Bellman update of the given state
(see the writeup and the Markov Models lecture for the formula to implement)

:param
state: the state that we are currently in
actions: the list of actions that may be taken from the state (note, not all actions are feasible
   from a given state)
transitions: a dictionary of transitions, where the key is a (state, action) tuple and
   the value is a list of (state, probability) tuples
rewards: a dictionary mapping states to a local (immediate) reward
cur_values: a dictionary mapping states to their current values
discount: the discount factor to be used

:return
res: the updated value of the state

"""
def bellman_update(state, actions, transitions, rewards, cur_values, discount):
    # BEGIN STUDENT CODE FOR PART 3
    evals = []
    for action in actions:
        if(state,action) in transitions:
            evals.append(expected_value(state,action,transitions,cur_values))
    return rewards[state] + discount*max(evals)
    # END STUDENT CODE FOR PART 3



class MDP:

    def __init__(self, states: List, actions: List[str], transitions: Dict, rewards: Dict, discount=0.95):
        self.states = states
        self.actions = actions
        self.transitions = transitions
        self.rewards = rewards
        self.discount = discount
        self.values = {}
        # Initialize rewards
        for key in rewards.keys(): self.values[key] = 0

    def best_action(self, state, values):
        max_value = -1e100
        bestAct = None
        for action in self.actions:
            if (self.transitions.get((state, action))):
                val = expected_value(state, action, self.transitions, values)
                if (val > max_value):
                    max_value = val; bestAct = action
        return bestAct

    #################
    # Helper functions needed for value iteration
    #################

    # Perform one iteration of value iteration, returns the new values and maximum residual
    def value_iter(self, values):
        new_values = {}
        max_res = 0
        for state in self.states:
            new_values[state] = bellman_update(state, self.actions, self.transitions, self.rewards,
                                               values, self.discount)
            res = abs(values[state] - new_values[state])
            if (res > max_res): max_res = res
        return (new_values, max_res)

    # Perform value iteration, return a policy (state/action mapping)
    def value_iteration(self, epsilon = 0.001, max_iters = 100):
        max_res = 100; num_iters = 0
        while max_res > epsilon and num_iters < max_iters:
            self.values, max_res = self.value_iter(self.values)
            num_iters += 1
        print("Value iteration: %d" %num_iters)
        policy = {}
        for state in self.states:
            policy[state] = self.best_action(state, self.values)
        return policy

    #################
    # Helper functions needed for policy iteration
    #################

    # Evaluate the policy for one iteration, returns the new values and maximum residual
    def policy_eval(self, policy, values):
        new_values = {}
        for state in self.states:
            value = self.rewards[state]
            action = policy.get(state)
            if (action): value += self.discount * expected_value(state, action, self.transitions, values);
            new_values[state] = value
        return new_values

    # Evaluate the policy by doing a number of modified value iteration steps (using policy_eval)
    def policy_evaluation(self, policy, epsilon = 0.1, max_iters = 10):
        max_res = 1e10; num_iters = 0;
        while max_res > epsilon and num_iters < max_iters:
            self.values = self.policy_eval(policy, self.values)
            num_iters += 1
        if (debugging): print("Policy evaluation: %d" %num_iters)

    # Perform one iteration of policy iteration, returns whether any policy action has changed
    def policy_iter(self, policy, epsilon, eval_iters):
        self.policy_evaluation(policy, epsilon, eval_iters)
        changed = False
        for state in self.states:
            action = policy[state]
            best_action = self.best_action(state, self.values)
            if (expected_value(state, best_action, self.transitions, self.values) > \
                expected_value(state, action, self.transitions, self.values)):
                policy[state] = best_action
                changed = True
        return changed

    # Perform policy iteration
    def policy_iteration(self, epsilon = 0.1, max_iters = 100, eval_iters = 10):
        # Initialize the policy
        policy = {}
        for state in self.states:
            # Make sure to initialize with a legal action for that state
            for action in self.actions:
                if (self.transitions.get((state, action))):
                    policy[state] = action
                    break
        changed = True; num_iters = 0
        while changed and num_iters < max_iters:
            changed = self.policy_iter(policy, epsilon, eval_iters)
            num_iters += 1
        print("Policy iteration: %d" % num_iters)
        return policy
