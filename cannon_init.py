''' Cannon game: First Assignment 1 for Scientific Computing at Roskilde University

 Program functionality description:

   The following program displays a (2000m broad and 1000m high) field with a blue canon (20m wide, 16m high) positioned
   200m from the left side of the field. The scaling factor is 0.5, thus the window is 1000 pixels x 500 pixels.
   The cannon's upper left corner is at position (200m,16m). The player can click to change the initial velocity of the
   cannon shot. Once the cannonball hits the ground, it explodes with a 200 m radius explosion. Hit the other player
   with the explosion to score a point. After 5 rounds the winner will be the player with the most points.


Program controls:
    Press q to quit,
          g to show/hide grid
          Click mouse1 to change velocity of ball

  Authors: S. Stefanovich, Maja H Kirkeby & Ulf R. Pedersen


'''

# Import modules
import pygame
import sys
import math
import numpy

# Initialize pygame
pygame.init()

# Define colors
BLACK = 0, 0, 0
WHITE = 255, 255, 255
BLUE = 0, 0, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
PINK = 255, 204, 229
PURPLE = 153, 0, 153
ORANGE = 255, 153, 51


# Define a frame rate
frames_per_second = 60

# Initialize real world parameters
g = 9.8   # Gravitational acceleration (m/s**2)
mass = 1  # Mass of projectile (kg)
D = 0.1 # Coefficient of drag
blast_field = 200.0 # blast field radius (m)

# Set parameters for time
speedup = 8    # in order to reduce waiting time for impact we speed up by increasing the timestep
t = 0.0        # time in seconds
dt = (1 / frames_per_second)*speedup  # time increment in seconds

width = 2000.0   # Position of wall to the right and width of the coordinate system
height = 1000.0  # Height of the coordinate system
x_grid = 100 # the interval of x-axis grid of the coordinate system
y_grid = 100  # the interval of y-axis grid of the coordinate system

scale_real_to_screen = 0.5 # scale from the real-world to the screen-coordinate system

turn_counter = 0 # round counter
score_1 = 0 # player 1 score
score_2 = 0 # player 2 score

def convert(real_world_x, real_world_y, scale=scale_real_to_screen, real_world_height=height):
    ''' conversion from real-world coordinates to pixel-coordinates '''
    return int(real_world_x*scale), int((real_world_height-real_world_y)*scale-1)

# initialize real world cannon(s):
# ================================
# The values for the cannon is kept in a dictionary called cannon1. The correctness of some of the functions depend
# on the cannon to have the specified keys defined (you can add other key-value pairs). The intention is that you
# can create extra cannons, i.e., dictionaries with the same keys and different values, and add those to the
# players-list.
# 315.0 m/s Cannonball, e.g., https://www.arc.id.au/CannonBallistics.html
# 120 m/s small gun https://en.wikipedia.org/w/index.php?title=Muzzle_velocity&oldid=970936654

cannon_width, cannon_height = 20, 16
cannon1 = {"x": 200,
           "y": 0+cannon_height,
           "vx": 84.85,  # ≈ 120 m/s angle 45
           "vy": 84.85,  # ≈ 120 m/s angle 45
           "width": cannon_width,
           "height": cannon_height,
           "color": BLUE,
           'ball_radius': 2,  # radius in meters
           'score' : 0
            }
cannon2 = {"x": 1800,
           "y": 0+cannon_height,
           "vx": -84.85,  # ≈ 120 m/s angle 45
           "vy": 84.85,  # ≈ 120 m/s angle 45
           "width": cannon_width,
           "height": cannon_height,
           "color": PINK,
           'ball_radius': 2,  # radius in meters
           'score' : 0
            }
# list of players
players = [cannon1,cannon2]

def calc_init_ball_pos(cannon):
    ''' Finds the center of the cannon '''
    return cannon['x'] + cannon['width']/2, cannon['y'] - cannon['height']/2

def draw_cannon(surface, cannon):
    ''' Draw the cannon (the barrel will be the length of the initial velocity of the ball '''
    rect = (
        convert(cannon['x'], cannon['y']),
        (cannon['width']*scale_real_to_screen, cannon['height']*scale_real_to_screen)
    )
    pygame.draw.rect(surface, cannon['color'], rect)
    cannon_center = calc_init_ball_pos(cannon)
    line_from = convert(cannon_center[0], cannon_center[1])
    line_to = convert(cannon_center[0]+cannon['vx']*scale_real_to_screen, cannon_center[1]+cannon['vy']*scale_real_to_screen)
    line_width = 2
    pygame.draw.line(surface, cannon['color'], line_from, line_to, line_width)

def is_inside_field(real_world_x, real_world_y, field_width=width):
    ''' Return true if input is within world '''
    # Note: there is no ceiling
    return 0 < real_world_x < field_width and real_world_y > 0

def draw_blast_field(surface, real_world_x, real_world_y):
    '''Draws a circle with the blast field radius'''
    x_pixel, y_pixel = convert(real_world_x, real_world_y)
    pygame.draw.circle(surface, ORANGE, (x_pixel, y_pixel), blast_field)

def is_player_hit(real_world_x, real_world_y, cannon):
    '''Returns true when a player is hit, otherwise false'''
    if real_world_x-blast_field < cannon['x'] < real_world_x+blast_field:
        return True
    return False

def random_wind():
    '''Generates a random wind velocity from -15 to 15 m/s.'''
    wind = numpy.random.uniform(-15, 15)
    return wind

def change_shot(cannon):
    '''Changes the shot position to be a vector from cannon center to where the mouse is '''
    x, y = pygame.mouse.get_pos()
    x_center, y_center = calc_init_ball_pos(cannon)
    new_vx, new_vy = x-x_center*scale_real_to_screen, -y+height*scale_real_to_screen-y_center
    cannon['vx'], cannon['vy'] = new_vx, new_vy
    return new_vx, new_vy


def draw_wind(surface, cannon, wind_velocity):
    ''' Draw an arrow showing a random wind velocity from -15 to 15. The velocity is shown 10x for clarity. '''

    line_from = convert(cannon['x'], cannon['y']+100)
    line_to = convert(cannon['x']+wind_velocity*10, cannon['y']+100)

    pygame.draw.line(surface,PURPLE,line_from,line_to,2)



# Create PyGame screen:
# 1. specify screen size
screen_width, screen_height = int(width*scale_real_to_screen), int(height*scale_real_to_screen)
# 2. define screen
screen = pygame.display.set_mode((screen_width, screen_height))
# 3. set caption
pygame.display.set_caption("CANNON GAME")

# Update pygames clock use the framerate
clock = pygame.time.Clock()


def draw_grid(surface, color, real_x_grid, real_y_grid, real_width=width, real_height=height):
    ''' Draw real-world grid on screen '''
    # vertical lines
    for i in range(int(real_width / real_x_grid)):
        pygame.draw.line(surface, color, convert(i * real_x_grid, 0),  convert(i * real_x_grid, real_height))
    # horizontal lines
    for i in range(int(real_height / y_grid)):
        pygame.draw.line(surface, color, convert(0 , i * real_y_grid ), convert(real_width, i * real_y_grid))

# Initialize game loop variables
running = True
shooting = False
show_grid = True
Hit = False
turn = 0

# Initialize projectile values (see also function below)
x, y = calc_init_ball_pos(players[turn])
vx = players[turn]['vx']  # x velocity in meters per second
vy = players[turn]['vy']  # y velocity in meters per second
ball_color = players[turn]['color']
ball_radius = players[turn]['ball_radius']
wind = random_wind() # x velocity in meters per second
x_hit, y_hit = 0,0

def change_player():
    ''' initialize the global variables of the projectile to be those of the players cannon '''
    global players, turn, x, y, vx, vy, ball_color, ball_radius, wind, x_hit, y_hit
    turn = (turn + 1) % len(players)   # will rotate through the list of players
    x, y = calc_init_ball_pos(players[turn])
    vx, vy = players[turn]['vx'], players[turn]['vy']
    ball_color = players[turn]['color']
    ball_radius = players[turn]['ball_radius']
    wind = random_wind()
    x_hit, y_hit = 0, 0

# Game loop:
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            show_grid = not show_grid
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: # 1.
            shooting = not shooting
        if pygame.mouse.get_pressed()[0]:
            vx, vy = change_shot(players[turn])

    # Check whether the ball is outside the field
    if not is_inside_field(x,y):
        x_hit, y_hit = x,y
        print(x_hit, y_hit)
        if is_player_hit(x_hit,y_hit,players[turn-1]): #checks if blast radius hit other player
            Hit = True
            players[turn]['score'] += 1
            print('HIT')

        change_player() # if there is only one player, the ball will restart at that players center
        turn_counter += 1
        shooting = not shooting # stops shooting between shots
        wind = random_wind() # changes wind direction


    # Game logic
    #   draw a background using screen.fill()
    screen.fill(BLACK)

    # draw grid
    if show_grid:
        draw_grid(screen, GREEN, x_grid, y_grid, width, height)

    # draw the player's cannon
    draw_cannon(screen, cannon1)
    draw_cannon(screen, cannon2)

    # draw wind direction arrow

    if turn == 0:
        draw_wind(screen, cannon1,wind)
    else:
        draw_wind(screen, cannon2, wind)

    # keep track of players' scores


    # end game when score 5 rounds are through, posts score.

    if turn_counter == 5*len(players):
        running = False
        print(f'GAME OVER: {int(turn_counter/2)} rounds')
        for i in range(len(players)):
            print(f'PLAYER {i+1} SCORE: {players[i]['score']}')
        print(f'Thanks for playing.')


    # convert the real-world coordinates to pixel-coordinates
    x_pix, y_pix = convert(x, y)
    ball_radius_pix = round(scale_real_to_screen * ball_radius)

    # draw ball using the pixel coordinates
    pygame.draw.circle(screen, ball_color, (x_pix,y_pix), ball_radius_pix)
    x_hit, y_hit = convert(x_hit, y_hit)
    if Hit:
        pygame.draw.circle(screen, ORANGE, (x_hit,y_hit), blast_field*scale_real_to_screen)


    # print time passed, position and velocity
    #print(f"time: {t}, pos: ({x,y}), vel: ({vx,vy}, pixel pos:({x_pix},{y_pix}))")

    if shooting:
        # update time passed, the projectile 's real-world acceleration, velocity,
        # position for the next time_step using the Leap-Frog algorithm

        # Apply force of gravitational acceleration and drag
        Fx = 0 - math.cos(math.pi/4)*D*(vx-wind)
        Fy = -mass*g - math.sin(math.pi/4)*D*vy

        # Compute acceleration
        ax = Fx/mass
        ay = Fy/mass

        # Update velocities from acceleration
        vx = vx + ax*dt
        vy = vy + ay*dt

        # Update positions from velocities
        x = x + vx * dt
        y = y + vy * dt

    # Redraw the screen
    pygame.display.flip()
    if Hit:
        pygame.time.delay(2000) #if a player is hit wait a bit before proceeding
    Hit = False


    # Limit the framerate (must be called in each iteration)
    clock.tick(frames_per_second)

# Close after the game loop
pygame.quit()
sys.exit()
