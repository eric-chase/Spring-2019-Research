import random
import sys
from utilities import get_configurations, get_obstacle_locations, get_start_states, get_target_states

width = 6
height = 6

class GridWorld(object):

    def __init__(self, width, height, start, targets, blocked):
        self.initial_state = start
        self.current_state = start[:] # Originally, the current states are the start states
        self.initial_state_list = list(start)
        self.width = width
        self.height = height
        self.targets = targets
        self.blocked = blocked
        # NOTE: The positions of the other robots should be included in blocked

        self.actions = ('n', 's', 'e', 'w')
        self.states = set()
        for x in range(width):
            for y in range(height):
                if (x,y) not in self.targets and (x,y) not in self.blocked:
                    self.states.add((x,y))

        # Parameters for the simulation
        self.success_prob = 1.0
        self.gamma = 0.9
        self.living_reward = -1.5

    """
    Calculate the reward of a target state (no longer a constant attribute)
    """
    def get_reward(self, i, state):
        reward = 0
        for j in range(len(self.initial_state)):
            if(j != i):
                reward += abs((state[0] - self.current_state[j][0]) +
                              (state[1] - self.current_state[j][1]))
        return reward
        
    #### Internal functions for running policies ###

    def get_transitions(self, state, action):
        """
        Return a list of (successor, probability) pairs that
        can result from taking action from state
        """
        result = []
        x,y = state
        remain_p = 0.0

        if action == "n":
            success = (x, y - 1)
            fail = [(x + 1, y), (x - 1, y)]
        elif action == "s":
            success = (x, y + 1)
            fail = [(x + 1, y), (x - 1, y)]
        elif action == "e":
            success = (x + 1, y)
            fail= [(x, y - 1), (x, y + 1)]
        elif action == "w":
            success = (x - 1, y)
            fail= [(x, y - 1), (x, y + 1)]
        else:
            return None
        
        if success[0] < 0 or success[0] > self.width - 1 or \
           success[1] < 0 or success[1] > self.height - 1 or \
           success in self.blocked: 
                remain_p += self.success_prob
        else: 
            result.append((success, self.success_prob))
        
        for i,j in fail:
            if i < 0 or i > self.width - 1 or \
               j < 0 or j > self.height - 1 or \
               (i, j) in self.blocked: 
                    remain_p += (1 - self.success_prob) / 2
            else:
                result.append(((i, j), (1 - self.success_prob) / 2))
           
        if remain_p > 0.0: 
            result.append(((x, y), remain_p))
        return result

    def move(self, state, action):
        """
        Return the state that results from taking this action
        """
        transitions = self.get_transitions(state, action)
        if(transitions == None):
            return None
        new_state = random.choices([i[0] for i in transitions], weights=[i[1] for i in transitions])
        return new_state[0]

    def simple_policy_rollout(self, policy):
        """
        Return (Boolean indicating success of trial, total rewards) pair
        """
        state = self.initial_state
        rewards = 0
        while True:
            if state in self.targets:
                return (True, rewards+self.target_reward)
            state = self.move(state, policy[state])
            rewards += self.living_reward

    def QValue_to_value(self, Qvalues):
        """
        Given a dictionary of q-values corresponding to (state, action) pairs,
        return a dictionary of optimal values for each state
        """
        values = {}
        for state in self.states:
            values[state] = -float("inf")
            for action in self.actions:
                values[state] = max(values[state], Qvalues[(state, action)])
        return values

    #### Some useful functions for you to visualize and test your MDP algorithms ###

    def test_policy(self, policy, t = 500):
        """
        Following the policy t times, return (Rate of success, average total rewards)
        """
        numSuccess = 0.0
        totalRewards = 0.0
        for i in range(t):
            result = self.simple_policy_rollout(policy)
            if result[0]:
                numSuccess += 1
            totalRewards += result[1]
        return (numSuccess / t, totalRewards / t)

    def gen_rand_set(width, height, size):
        """
        Generate a random set of grid spaces.
        Useful for creating randomized maps.
        """
        mySet = set([])
        while len(mySet) < size:
            mySet.add((random.randint(0, width - 1), random.randint(0, height - 1)))
        return mySet

    def print_map(self, policy = None):
        """
        Print out a map of the environment, where * indicates start state,
        # indicates blocked states.
        A policy may optionally be provided, which will be printed out on the map as well.
        """
        sys.stdout.write(" ")
        for i in range(8 * (self.width - 1)):
            sys.stdout.write("-")
        sys.stdout.write("\n")
        for j in range(self.height):
            sys.stdout.write("|")
            for i in range(self.width):
                if (i, j) in self.targets:
                    if(i != width - 1):
                        sys.stdout.write("T\t")
                    else:
                        sys.stdout.write("T")
                elif (i, j) in self.blocked:
                    sys.stdout.write("#\t")
                else:
                    if policy and (i, j) in policy:
                        a = policy[(i, j)]
                        if a == "n":
                            sys.stdout.write("^")
                        elif a == "s":
                            sys.stdout.write("v")
                        elif a == "e":
                            sys.stdout.write(">")
                        elif a == "w":
                            sys.stdout.write("<")
                        sys.stdout.write("\t")
                    elif (i, j) in self.initial_state:
                        sys.stdout.write(str(self.initial_state_list.index((i, j)) + 1) + "\t")
                    else:
                        sys.stdout.write(".\t")
            sys.stdout.write("|")
            sys.stdout.write("\n")
        sys.stdout.write(" ")
        for i in range(8 * (self.width - 1)):
            sys.stdout.write("-")
        sys.stdout.write("\n")

    def print_values(self, values):
        """
        Given a dictionary {state: value}, print out the values on a grid
        """
        for j in range(self.height):
            for i in range(self.width):
                if (i, j) in self.holes:
                    value = self.hole_reward
                elif (i, j) in self.targets:
                    value = self.target_reward
                elif (i, j) in self.blocked:
                    value = 0.0
                else:
                    value = values[(i, j)]
                print("%10.2f" % value, end = '')
            print()

    def extract_policy(self, i, values):
        """
        Given state values, return the best policy.
        """
        policy = {}
        for state in values:
            max_value = float("-inf")
            for action in self.actions:
                action_value = 0
                for transition in self.get_transitions(state, action):
                    reward = self.living_reward
                    if(transition[0] in self.targets):
                        action_value += transition[1] * (reward + (self.gamma * self.get_reward(i, transition[0])))
                    else:
                        action_value += transition[1] * (reward + (self.gamma * values[transition[0]]))

                if(action_value >= max_value):
                    max_value = action_value
                    policy[state] = action

        return policy

    def Qlearner(self, alpha, epsilon, num_trials):
        """
        Implement Q-learning with the alpha and epsilon parameters provided.
        Runs number of episodes equal to num_trials.
        """
        # Initially set all Q-values to 0
        Qvalues = [{} for robot in self.initial_state]
        for state in self.states:
            for action in self.actions:
                for i in range(len(self.initial_state)):
                    Qvalues[i][(state, action)] = 0
        
        # NOTE: We can get away with planning for each robot separately
        for i in range(len(self.initial_state)):
            # For a trial to complete, all robots must reach a goal state
            for j in range(num_trials):
                goal_reached = False
                while(goal_reached == False):
                    position = self.current_state[i]
                    selected_action = None
                    if(random.random() < epsilon): # Explore
                        selected_action = self.actions[random.randint(0, 3)]
                    else: # Don't explore
                        action_value = float("-inf")
                        for action in self.actions: # Select action
                            if((Qvalues[i][(position, action)] > action_value) and
                               (self.move(position, action) not in self.current_state)):
                                action_value = Qvalues[i][(position, action)]
                                selected_action = action
                    new_position = self.move(position, selected_action)
                    if(new_position == None):
                        continue
               
                    if(new_position in self.targets):
                        Qvalues[i][(position, selected_action)] = ((1 - alpha) * Qvalues[i][(position, selected_action)]) + (alpha * (self.living_reward + (self.gamma * self.get_reward(i, new_position))))
                        goal_reached = True # Goal reached
                    else:
                        action_value = float("-inf")
                        for action in self.actions: # Select action
                            if(Qvalues[i][(new_position, action)] > action_value):
                                action_value = Qvalues[i][(new_position, action)]
                        Qvalues[i][(position, selected_action)] = ((1 - alpha) * Qvalues[i][(position, selected_action)]) + (alpha * (self.living_reward + (self.gamma * action_value)))
        
                    self.current_state[i] = new_position # Move the robot now that the previos Q-value has been updated
                self.current_state[i] = self.initial_state[i][:] # Reset the robot location
            
            # Set the current position of the robot to its best target
            learned_values = grid_world.QValue_to_value(Qvalues[i])
            learned_policy = grid_world.extract_policy(i, learned_values)
            while(self.current_state[i] not in self.targets):
                self.current_state[i] = self.move(self.current_state[i], learned_policy[self.current_state[i]])

        return Qvalues  

if __name__ == "__main__":
    # NOTE: The distance of the goal states (T's) are determined by 'border_dist' below
    border_dist = 2 # Goal separation
    configuration_size = (2, 2)

    for config in get_configurations(configuration_size):
        """
        Create a GridWorld simulation (NOTE: The world should be the same size as the
        jammed configuration state).
        
        The map can be thought of as a cutout of the larger map in the D* Lite simulation.
        """
        width = configuration_size[0] + (2 * border_dist)
        height = configuration_size[1] + (2 * border_dist)
        start = get_start_states(config, border_dist)
        targets = set(get_target_states(config, border_dist))
        blocked = set(get_obstacle_locations(config, border_dist))
        grid_world = GridWorld(width, height, start, targets, blocked)
        
        print("Original map:")
        grid_world.print_map()

        Qvalues = grid_world.Qlearner(alpha = 0.5, epsilon = 0.5, num_trials = 1000)
        for i in range(len(Qvalues)):
            learned_values = grid_world.QValue_to_value(Qvalues[i])
            learned_policy = grid_world.extract_policy(i, learned_values)
            print("Learned map for robot {}:".format(i + 1))
            grid_world.print_map(learned_policy)