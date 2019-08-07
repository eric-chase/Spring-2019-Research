import pygame
import random
from grid import SquareGrid
from dstarlite import DStarLite

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (77, 77, 51)
BLUE = (0, 0, 80)

# Define a robot color dictionary
r_colors = {
    0: GREEN,
    1: RED,
    2: (255, 192, 203), # PINK
    3: BLUE
}
# Define a robot dictionary for text position onscreen
r_text = {
    0: (1, 1),
    1: (3, 1),
    2: (1, 3),
    3: (3, 3)
}

# Initialize pygame
pygame.init()

num_robots = 2
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
    
    # Set up the start and goal states for each robot
    for i in range(num_robots):        
        # Prevent any start and goal states from overlapping
        while(True):
            isValid = True
            start = (random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
            goal = (random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
            # Make sure the start and goal states do not overlap
            while(goal == start):
                goal = (random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
            for j in range(len(param_list)):
                if(param_list[j][0] == start or param_list[j][1] == start or
                   param_list[j][0] == goal or param_list[j][1] == goal):
                    isValid = False
                    
            # Add the start/goal states for the robot to 'problem_states'
            if isValid:
                param_list.append([start, goal])
                break
    
    # Generate random obstacles (limited to 10% of the map size)
    initial_obstacles = []
    for i in range(0, int((X_DIM * Y_DIM) * (random.randint(5, 10) / 100))):
        obstacle_coords = (random.randint(0, X_DIM - 1), random.randint(0, Y_DIM - 1))
        isValid = True
        # Prevent objects on the start or goal locations
        for j in range(num_robots):
            start = param_list[j][0]
            goal = param_list[j][1]
            if(start == obstacle_coords or goal == obstacle_coords):
                isValid = False
                break
        if isValid:
            initial_obstacles.append(obstacle_coords)
    
    # Initialize a D* Lite search for each robot
    for i in range(num_robots):
        g = SquareGrid(X_DIM, Y_DIM, eightway = True)
        start = param_list[i][0]
        goal = param_list[i][1]
        for obstacle in initial_obstacles:
            g.walls.add(obstacle)
        dstar = DStarLite(g, start, goal)
        param_list[i].append(dstar)
        param_list[i].append(False) # Mark the search as incomplete

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
                    goal = param_list[i][1]
                    dstar = param_list[i][2]
                    s_new = next(dstar.move_to_goal())[0]
                    if s_new == goal: # Search is complete
                        if(param_list[i][3] == False):
                            print("Goal {} Reached!".format(i + 1))
                            param_list[i][3] = True

                # Check if all robots are done (game is complete)
                for i in range(num_robots):
                    complete = param_list[i][3]
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
                g = param_list[0][2].real_graph
                isValid = True
                for i in range(num_robots):
                    goal = param_list[i][1]
                    if((column, row) == goal):
                        isValid = False
                if(isValid == True):
                    for j in range(num_robots):
                        param_list[j][2].real_graph.walls.add((column, row))

        # Set the screen background
        screen.fill(BLACK)

        # Draw the grid
        g = param_list[0][2].real_graph
        for row in range(Y_DIM):
            for column in range(X_DIM):
                if((column, row) in g.walls):
                    pygame.draw.rect(screen, GRAY, [(MARGIN + WIDTH) * column + MARGIN,
                                     (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
                else:
                    pygame.draw.rect(screen, WHITE, [(MARGIN + WIDTH) * column + MARGIN,
                                     (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT])
        
        # Draw the current path
        for i in range(num_robots):
            dstar = param_list[i][2]
            back_pointers = dstar.compute_shortest_path()[0]
            s_current = dstar.position
            path = []
            while(s_current != dstar.goal):
                s_current = back_pointers[s_current]
                path.insert(0, s_current)
             
            r_color = r_colors[i % 5]
            for j in range(1, len(path)):
                text = basicfont.render(str(j), True, r_color)
                textrect = text.get_rect()
                textrect.centerx = int(path[j][0] * (WIDTH + MARGIN) + WIDTH / 4 * r_text[i][0]) + MARGIN
                textrect.centery = int(path[j][1] * (HEIGHT + MARGIN) + HEIGHT / 4 * r_text[i][1]) + MARGIN
                screen.blit(text, textrect)

        # Fill in goal cells with GOLD
        for i in range(num_robots):
            goal_coords = param_list[i][1]
            pygame.draw.rect(screen, (255, 215, 0), [(MARGIN + WIDTH) * goal_coords[0] + MARGIN,
                                         (MARGIN + HEIGHT) * goal_coords[1] + MARGIN, WIDTH, HEIGHT])
            text = goalfont.render("G", True, r_colors[i % 10])
            textrect = text.get_rect()
            textrect.centerx = int(goal_coords[0] * (WIDTH + MARGIN) + WIDTH / 2) + MARGIN
            textrect.centery = int(goal_coords[1] * (HEIGHT + MARGIN) + HEIGHT / 2) + MARGIN
            screen.blit(text, textrect)

        # Draw moving robots, based on pos_coords
        for i in range(num_robots):
            r_color = r_colors[i % 5]
            pos_coords = param_list[i][2].position
            robot_center = [int(pos_coords[0] * (WIDTH + MARGIN) + WIDTH / 2) +
                            MARGIN, int(pos_coords[1] * (HEIGHT + MARGIN) + HEIGHT / 2) + MARGIN]
            #pygame.draw.circle(screen, r_color, robot_center, int(WIDTH / 2) - 2)
            pygame.draw.rect(screen, r_color,
                             [(MARGIN + WIDTH) * pos_coords[0] + MARGIN,
                             (MARGIN + HEIGHT) * pos_coords[1] + MARGIN, WIDTH, HEIGHT])

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