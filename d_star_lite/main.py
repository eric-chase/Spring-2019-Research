import pygame
import random
from grid import GridWorld
from utils import stateNameToCoords
from d_star_lite import initDStarLite, moveAndRescan, nextInShortestPath

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY1 = (145, 145, 102)
GRAY2 = (77, 77, 51)
BLUE = (0, 0, 80)

# Define a general color dictionary
colors = {
    0: WHITE,
    1: GREEN,
    -1: GRAY1,
    -2: GRAY2
}
# Define a robot color dictionary
r_colors = {
    0: GREEN,
    1: RED,
    2: (255, 192, 203), # PINK
    3: BLUE,
    4: (255, 128, 0), # ORANGE
    5: (139, 69, 19), # BROWN
    6: (128, 0, 128), # PURPLE
    7: (255, 255, 0), # YELLOW
    8: (64, 224, 208), # TURQUOISE
    9: (0, 100, 0) # DARK GREEN
}

# Variables used for learning in the RL program
blocked = set()
targets = set()

# Initialize pygame
pygame.init()

num_robots = 3
X_DIM = 15
Y_DIM = 15
VIEWING_RANGE = 2
# This sets the WIDTH and HEIGHT of each grid location (default size is 40)
WIDTH, HEIGHT = 40, 40
# Prevent window from going off of the screen
while((WIDTH * Y_DIM) > (40 * 19)):
    WIDTH -= 1
    HEIGHT -= 1
# This sets the margin between each cell
MARGIN = 1

# Set the HEIGHT and WIDTH of the screen
WINDOW_SIZE = [(WIDTH + MARGIN) * X_DIM + MARGIN,
               (HEIGHT + MARGIN) * Y_DIM + MARGIN]
screen = pygame.display.set_mode(WINDOW_SIZE)

# Set title of screen
pygame.display.set_caption("D* Lite Path Planning")

# Loop until the user clicks the close button
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

if __name__ == "__main__":
    param_list = []
    for i in range(num_robots):
        graph = GridWorld(X_DIM, Y_DIM)
        k_m = 0
        queue = []
        complete = False
        
        # Prevent any start and goal states from overlapping
        while(True):
            isValid = True
            s_start = "x{}y{}".format(random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
            s_goal = "x{}y{}".format(random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
            # Make sure the start and goal states do not overlap
            while(s_goal == s_start):
                s_goal = "x{}y{}".format(random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
            goal_coords = stateNameToCoords(s_goal)
            
            for j in range(len(param_list)):
                if((param_list[j][1] == s_start) or (param_list[j][2] == s_goal) or
                   (param_list[j][1] == s_goal) or (param_list[j][2] == s_start)):
                    isValid = False
            if(isValid == True): # D* Lite queue is ready to be set up
                # Add the D* parameters for the robot to 'param_list'
                graph.setStart(s_start)
                graph.setGoal(s_goal)
                s_last = s_start
                s_current = s_start
                pos_coords = stateNameToCoords(s_current)
                graph, queue, k_m = initDStarLite(graph, queue, s_start, s_goal, k_m)
                param_list.append([graph, s_start, s_goal, goal_coords, k_m,
                                   s_last, queue, s_current, pos_coords, complete])
                break
    
    # Generate random obstacles (limited to 10% of the map size)
    initial_obstacles = []
    obstacles = []
    for i in range(0, int((X_DIM * Y_DIM) * (random.randint(5, 10) / 100))):
        row = random.randint(0, Y_DIM - 1)
        column = random.randint(0, X_DIM - 1)
        obstacle_coords = (column, row)
        # Prevent objects on the start or goal locations
        for i in range(num_robots):
            s_start = param_list[i][1]
            goal_coords = param_list[i][3]
            if((tuple(stateNameToCoords(s_start)) != obstacle_coords) and
               (tuple(goal_coords) != obstacle_coords)):
                initial_obstacles.append(obstacle_coords)
                obstacles.append(obstacle_coords)

    basicfont = pygame.font.SysFont('Comic Sans MS', 12)
    goalfont = pygame.font.SysFont('Comic Sans MS', 16)
    init_event = True

    # -------- Main Program Loop -----------
    while not done:
        events = pygame.event.get()
        if((len(events) == 0) and (init_event == False)):
            continue
        for event in events: # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done = True # Flag that we are done so we exit this loop
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                for i in range(num_robots):
                    graph = param_list[i][0]
                    queue = param_list[i][6]
                    s_current = param_list[i][7]
                    k_m = param_list[i][4]
                    s_new, k_m = moveAndRescan(graph, queue, s_current, VIEWING_RANGE, k_m)
                    param_list[i][4] = k_m
                    if s_new == 'goal': # Search is complete
                        old_complete_value = param_list[i][9]
                        param_list[i][9] = True
                        if(old_complete_value == False):
                            print("Goal {} Reached!".format(i + 1))
                    else:
                        param_list[i][7] = s_new
                        param_list[i][8] = stateNameToCoords(param_list[i][7])

                # Check if all robots are done (game is complete)
                for i in range(num_robots):
                    complete = param_list[i][9]
                    if(complete == False):
                        break
                    if(i == num_robots - 1):
                        done = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # User clicks the mouse. Get the position.
                pos = pygame.mouse.get_pos()
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)
                # Cross out that location
                graph_1 = param_list[0][0]
                if(graph_1.cells[row][column] == 0):
                    isValid = True
                    for i in range(num_robots):
                        goal_coords = param_list[i][3]
                        if([column, row] == goal_coords):
                            isValid = False
                    if(isValid == True):
                        for i in range(num_robots):
                            param_list[i][0].cells[row][column] = -1
                            obstacles.append((column, row))
                # Enable that location (only works for not yet observed objects)
                elif(graph_1.cells[row][column] == -1):
                    for i in range(num_robots): 
                        param_list[i][0].cells[row][column] = 0    
            
            elif(init_event == True):
                # Draw random obstacles (limited to 10% of the map size)
                # NOTE: The user can also add obstacles as we go (to simulate dynamic environment behavior)
                for i in range(num_robots):
                    graph = param_list[i][0]
                    for obstacle in initial_obstacles:
                        column = obstacle[0]
                        row = obstacle[1]
                        if(graph.cells[row][column] == 0):
                            graph.cells[row][column] = -1
                init_event = False

        # Set the screen background
        screen.fill(BLACK)

        # Draw the grid
        combined_graph = GridWorld(X_DIM, Y_DIM)
        combined_graph.cells = param_list[0][0].cells[:]
        scanned_obstacles = []
        for i in range(num_robots): 
            for row in range(Y_DIM):
                for column in range(X_DIM):
                    graph = param_list[i][0]
                    if(graph.cells[row][column] == -2):
                        scanned_obstacles.append((row, column))
        for obstacle in scanned_obstacles:
            combined_graph.cells[obstacle[0]][obstacle[1]] = -2
        for row in range(Y_DIM):
            for column in range(X_DIM):
                pygame.draw.rect(screen, colors[combined_graph.cells[row][column]],
                                 [(MARGIN + WIDTH) * column + MARGIN,
                                  (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
    
        # Draw the current path
        for i in range(num_robots):
            s_current = param_list[i][7]
            graph = param_list[i][0]
            
            if(s_current != graph.goal):
                path_found = False
                next_node = s_current
                counter = 0
                r_color = r_colors[i % 10]
                path = set()
                
                while((path_found == False) and (counter < 100)):                
                    next_node = nextInShortestPath(graph, next_node)
                    if(next_node is None):
                        break
                    path.add(next_node)
                    coordinates = next_node.split('x')[1].split('y')
                    column = int(coordinates[0])
                    row = int(coordinates[1])
                    counter += 1
                    if(next_node == graph.goal):
                        path_found = True
                    else:
                        text = basicfont.render(str(graph.graph[next_node].g), True, r_color)
                        textrect = text.get_rect()
                        textrect.centerx = int(column * (WIDTH + MARGIN) + WIDTH / 2) + MARGIN
                        textrect.centery = int(row * (HEIGHT + MARGIN) + HEIGHT / 2) + MARGIN
                        screen.blit(text, textrect)
                # Check if the length of path is 2 (could mean that the robot is stuck)
                if((len(path) == 2) and (counter == 100) or (next_node == None)):
                    atGoal = False
                    goal_coord = param_list[i][3]
                    pos_coord = param_list[i][8]
                    for child in graph.graph[s_current].children:
                        child_coord = stateNameToCoords(child)
                        # Stuck next to goal
                        if(((pos_coord[0] == goal_coord[0]) and ((pos_coord[1] == goal_coord[1] + 1) or
                           (pos_coord[1] == goal_coord[1] - 1))) or ((pos_coord[1] == goal_coord[1]) and
                           ((pos_coord[0] == pos_coord[0] + 1) or (pos_coord[0] == goal_coord[0] - 1)))):
                            param_list[i][8] = param_list[i][3] # One of the children is the goal
                            param_list[i][7] = param_list[i][2]
                            num_blocks = 0
                            atGoal = True
                    # Stuck (not next to goal)
                    if(atGoal == False):
                        correct_children = [[pos_coord[0] + 1, pos_coord[1]], [pos_coord[0] - 1, pos_coord[1]],
                                            [pos_coord[0], pos_coord[1] + 1], [pos_coord[0], pos_coord[1] - 1]]
                        # Remove children who are out of range
                        correct_children = [child for child in correct_children if child[0] < X_DIM]
                        correct_children = [child for child in correct_children if child[1] < Y_DIM]
                        # NEED TO PREVENT THIS BEING OUT OF RANGE
                        min_child = None
                        min_dist = float('inf')
                        for child in correct_children:
                            child_state = "x{}y{}".format(child[0], child[1])
                            if((param_list[i][0].cells[child[1]][child[0]] == 0)):
                                #(child_state not in path)):
                                man_dist = abs(child[0] - goal_coord[0]) + abs(child[1] - goal_coord[1])
                                if(man_dist <= min_dist):
                                    min_dist = man_dist
                                    min_child = child
                        param_list[i][7] = "x{}y{}".format(min_child[0], min_child[1])
                        param_list[i][8] = min_child
                        num_blocks = 0

        # Fill in goal cells with GOLD
        for i in range(num_robots):
            goal_coords = param_list[i][3]
            pygame.draw.rect(screen, (255, 215, 0), [(MARGIN + WIDTH) * goal_coords[0] + MARGIN,
                                         (MARGIN + HEIGHT) * goal_coords[1] + MARGIN, WIDTH, HEIGHT])
            text = goalfont.render("G", True, r_colors[i % 10])
            textrect = text.get_rect()
            textrect.centerx = int(goal_coords[0] * (WIDTH + MARGIN) + WIDTH / 2) + MARGIN
            textrect.centery = int(goal_coords[1] * (HEIGHT + MARGIN) + HEIGHT / 2) + MARGIN
            screen.blit(text, textrect)

        # Draw moving robots, based on pos_coords
        for i in range(num_robots):
            r_color = r_colors[i % 10]
            pos_coords = param_list[i][8]
            robot_center = [int(pos_coords[0] * (WIDTH + MARGIN) + WIDTH / 2) +
                            MARGIN, int(pos_coords[1] * (HEIGHT + MARGIN) + HEIGHT / 2) + MARGIN]
            pygame.draw.circle(screen, r_color, robot_center, int(WIDTH / 2) - 2)

            # Draw robot viewing ranges
            pygame.draw.rect(
                screen, BLUE, [robot_center[0] - VIEWING_RANGE * (WIDTH + MARGIN), 
                robot_center[1] - VIEWING_RANGE * (HEIGHT + MARGIN), 
                2 * VIEWING_RANGE * (WIDTH + MARGIN), 2 * VIEWING_RANGE * (HEIGHT + MARGIN)], 2)

        # Limit to 60 frames per second
        clock.tick(20)

        # Update the screen with what is drawn
        pygame.display.flip()

    # Be IDLE friendly. Without this line, the program will 'hang' on exit.
    pygame.quit()