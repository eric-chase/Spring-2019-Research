import numpy as np
from itertools import product

# 'configuration_size' is a tuple corresponding to the size of the jam configuration,
# given by (row, column)    
def get_configurations(configuration_size):
    """
    Given a configuration size, return a list of all possible configurations
    """
    symbols = ['X', 'o', 'r']
    size = configuration_size[0] * configuration_size[1]
    
    # Holds all valid configurations so far (in string form according to our naming
    # convention). This is what gets returned.
    configurations = set()
    # Holds all valid configurations so far (as nested tuple structures). This is
    # used for permutation checking.
    arrays = set()
    perms = list(set(product(symbols, repeat = size)))
    for perm in perms:
        config = ','.join([perm[i - 1] if (i % configuration_size[0] != 0) else \
                           (perm[i - 1] + ',_') for i in range(1, len(perm) + 1)])
        config = config[:len(config) - 2]
        
        if(config.count('r') < 2):
            continue
        
        r_pos = [i for i, char in enumerate(config) if char == 'r']
        is_valid = True
        for i in r_pos:
            found_adjacent = False
            for j in r_pos:
                if((i != j) and ((abs(i - j) == 2) or (abs(i - j) == (4 + ((configuration_size[0] - 1) * 2))))):
                    found_adjacent = True
                    continue
            if(found_adjacent == False):
                is_valid = False
                break
                
        if(is_valid == True):
            configurations.add(config)
            
            # Now check if the configuration is a permutation of one we already know
            array = np.array([line.split(",") for line in config.split(",_,")])
            curr_arrays = set([tuple(tuple(x) for x in array.tolist()), 
                               tuple(tuple(x) for x in array[::-1].tolist()),
                               tuple(tuple(x) for x in array.transpose().tolist()),
                               tuple(tuple(x) for x in array[::-1].transpose().tolist()),
                               tuple(tuple(x) for x in array.transpose()[::-1].tolist())])
            is_perm = False
            for array in curr_arrays:
                if(array in arrays):
                    configurations.remove(config) # Remove configuration
                    is_perm = True
                    break
            if(is_perm == False): # No permutation found
                arrays = arrays | curr_arrays
    
    return(list(configurations))

# Get the obstalce locations for a configuration
def get_obstacle_locations(configuration, border_dist):
    """
    Given a configuration, return a list of all obstacle locations (marked by 'X')
    """
    obstacles = []
    config = [line.split(",") for line in configuration.split(",_,")]
    for i in range(len(config)):
        for j in range(len(config[i])):
            if(config[i][j] == 'X'):
                obstacles.append((i + border_dist, j + border_dist))
    return(obstacles)

def get_start_states(configuration, border_dist):
    """
    Given a configuration, return a list of all robot start states (marked by 'r')
    """
    starts = []
    config = [line.split(",") for line in configuration.split(",_,")]
    for i in range(len(config)):
        for j in range(len(config[i])):
            if(config[i][j] == 'r'):
                starts.append((i + border_dist, j + border_dist))
    return(starts)

def get_target_states(configuration, border_dist):
    """
    Given a configuration, return a list of all target states (i.e. the states that
    form a border around the configration at distance 'border_dist')
    """
    targets = []
    offset = 2 * border_dist
    config = [line.split(",") for line in configuration.split(",_,")]
    for i in range(len(config) + offset):
        for j in range(len(config[1]) + offset):
            if((i == 0) or (i == len(config) + (offset - 1)) or (j == 0) or
               (j == len(config[1]) + (offset - 1))):
                targets.append((i, j))
    return(targets)

if __name__ == "__main__":
    print(get_configurations((3, 3)))