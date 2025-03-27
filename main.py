import pygame
import sys
import math
import random  


# Init
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()  # Dynamically get screen size
pygame.display.set_caption("ISE Ball Physics Game")
clock = pygame.time.Clock()

# Constants
WHITE = (255, 255, 255)
RED = (220, 50, 50)
BLUE = (50, 100, 255)
ORANGE = (255, 140, 0)
GREEN = (50, 255, 50)
GROUND_Y = HEIGHT - 30

font = pygame.font.SysFont("Arial", 30)
goal_font = pygame.font.SysFont("Arial", 100, bold=True)


# Game State
gravity = 0.5
bounciness = -0.8
score_left = 0
score_right = 0
goal_scored = False
goal_time = 0
GOAL_PAUSE_DURATION = 2000  # milliseconds
goal_text_x = -200  # Start off-screen
goal_text_speed = 20



# Ball settings
ball_radius = 30
ball_pos = [WIDTH // 2, 100]
ball_vel = [0, 0]

# Player settings
player_radius = 30
player_pos = [WIDTH // 4, GROUND_Y - player_radius]
player_vel = [0, 0]
player_jump = -10
player_speed = 6
on_ground = True

# Enemy bot settings
enemy_radius = 30
enemy_pos = [3 * WIDTH // 4, GROUND_Y - enemy_radius]
enemy_vel = [0, 0]
enemy_jump = -10
enemy_speed = 10
enemy_on_ground = False

# Goal dimensions
goal_width = 100
goal_height = 150
goal_bar_thickness = 10

# Goal posts
left_post = pygame.Rect(0, GROUND_Y - goal_height, goal_bar_thickness, goal_height)
right_post = pygame.Rect(WIDTH - goal_bar_thickness, GROUND_Y - goal_height, goal_bar_thickness, goal_height)

# Goal top bars
left_bar = pygame.Rect(0, GROUND_Y - goal_height, goal_width, goal_bar_thickness)
right_bar = pygame.Rect(WIDTH - goal_width, GROUND_Y - goal_height, goal_width, goal_bar_thickness)

# Goal scoring zone (open part)
left_goal_zone = pygame.Rect(goal_bar_thickness, GROUND_Y - goal_height + goal_bar_thickness,
                             goal_width - goal_bar_thickness, goal_height - goal_bar_thickness)
right_goal_zone = pygame.Rect(WIDTH - goal_width, GROUND_Y - goal_height + goal_bar_thickness,
                              goal_width - goal_bar_thickness, goal_height - goal_bar_thickness)

def reset_ball():
    global ball_pos, ball_vel
    ball_pos = [WIDTH // 2, 50]
    ball_vel = [0, 0]

# Collision helper
def resolve_circle_collision(pos1, vel1, r1, pos2, vel2, r2, kick=False):
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    distance = math.hypot(dx, dy)
    min_dist = r1 + r2

    if distance < min_dist:
        if distance == 0:
            distance = 0.1
        nx, ny = dx / distance, dy / distance
        overlap = min_dist - distance
        pos1[0] += nx * overlap
        pos1[1] += ny * overlap
        bounce_force = 10 if kick else 4
        vel1[0] += nx * bounce_force
        vel1[1] += ny * bounce_force

def resolve_circle_rect_collision(circle_pos, circle_vel, radius, rect):
    closest_x = max(rect.left, min(circle_pos[0], rect.right))
    closest_y = max(rect.top, min(circle_pos[1], rect.bottom))

    dx = circle_pos[0] - closest_x
    dy = circle_pos[1] - closest_y
    distance = math.hypot(dx, dy)

    if distance < radius:
        if distance == 0:
            distance = 0.1
        nx = dx / distance
        ny = dy / distance
        overlap = radius - distance
        circle_pos[0] += nx * overlap
        circle_pos[1] += ny * overlap
        bounce_force = 4
        circle_vel[0] += nx * bounce_force
        circle_vel[1] += ny * bounce_force

    

# Main loop
running = True
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_EQUALS:  # = key
                running = False


    keys = pygame.key.get_pressed()

    # Player Movement
    if keys[pygame.K_a] and player_pos[0] - player_radius > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_d] and player_pos[0] + player_radius < WIDTH:
        player_pos[0] += player_speed
    if keys[pygame.K_SPACE] and on_ground:
        player_vel[1] = player_jump
        on_ground = False

    # AI Movement
    if ball_pos[0] > enemy_pos[0] + 10 and enemy_pos[0] + enemy_radius < WIDTH:
        enemy_pos[0] += enemy_speed
    elif ball_pos[0] < enemy_pos[0] - 10 and enemy_pos[0] - enemy_radius > 0:
        enemy_pos[0] -= enemy_speed

    if ball_pos[1] < enemy_pos[1] and enemy_on_ground:
        enemy_vel[1] = enemy_jump
        enemy_on_ground = False

    # Apply Gravity & Movement
    for pos, vel, radius in [(player_pos, player_vel, player_radius), (enemy_pos, enemy_vel, enemy_radius)]:
        vel[1] += gravity
        pos[1] += vel[1]
        if pos[1] >= GROUND_Y - radius:
            pos[1] = GROUND_Y - radius
            vel[1] = 0
            if pos == player_pos:
                on_ground = True
            else:
                enemy_on_ground = True

    ball_vel[1] += gravity
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    if ball_pos[1] >= GROUND_Y - ball_radius:
        ball_pos[1] = GROUND_Y - ball_radius
        ball_vel[1] *= bounciness

    if ball_pos[0] <= ball_radius or ball_pos[0] >= WIDTH - ball_radius:
        ball_vel[0] *= -1

    # Keep inside screen
    player_pos[0] = max(player_radius, min(WIDTH - player_radius, player_pos[0]))
    enemy_pos[0] = max(enemy_radius, min(WIDTH - enemy_radius, enemy_pos[0]))

    # Collisions
    resolve_circle_collision(ball_pos, ball_vel, ball_radius, player_pos, player_vel, player_radius, keys[pygame.K_k])
    resolve_circle_collision(ball_pos, ball_vel, ball_radius, enemy_pos, enemy_vel, enemy_radius, kick=True)
    # Prevent player and enemy from overlapping
    resolve_circle_collision(player_pos, player_vel, player_radius, enemy_pos, enemy_vel, enemy_radius)


    #Bounce off bar or post 
    ball_rect = pygame.Rect(ball_pos[0] - ball_radius, ball_pos[1] - ball_radius, ball_radius * 2, ball_radius * 2)

    # Realistic bar collision
    resolve_circle_rect_collision(ball_pos, ball_vel, ball_radius, left_bar)
    resolve_circle_rect_collision(ball_pos, ball_vel, ball_radius, right_bar)
    resolve_circle_rect_collision(player_pos, player_vel, player_radius, left_bar)
    resolve_circle_rect_collision(enemy_pos, enemy_vel, enemy_radius, left_bar)
    resolve_circle_rect_collision(player_pos, player_vel, player_radius, right_bar)
    resolve_circle_rect_collision(enemy_pos, enemy_vel, enemy_radius, right_bar)
    resolve_circle_rect_collision(ball_pos, ball_vel, ball_radius, left_post)
    resolve_circle_rect_collision(ball_pos, ball_vel, ball_radius, right_post)

    # Goal Detection
    ball_top = ball_pos[1] - ball_radius
    bar_limit_y = GROUND_Y - goal_height + goal_bar_thickness

    current_time = pygame.time.get_ticks()

    if not goal_scored:
        if left_goal_zone.contains(ball_rect):
            score_right += 1
            goal_scored = True
            goal_time = current_time
            goal_text_x = -200  # Reset text position

        elif right_goal_zone.contains(ball_rect):
            score_left += 1
            goal_scored = True
            goal_time = current_time
            goal_text_x = -200  # Reset text position

    # Animate goal text
    if goal_scored:
        goal_text_x += goal_text_speed

        # Inside your main loop, during goal_scored:
        shake_offset_x = random.randint(-5, 5)
        shake_offset_y = random.randint(-5, 5)

        goal_display = goal_font.render("GOAL!", True, (255, 215, 0))
        screen.blit(goal_display, (goal_text_x + shake_offset_x, 60 + shake_offset_y))


        # After 2 seconds, reset ball
        if current_time - goal_time >= GOAL_PAUSE_DURATION:
            reset_ball()
            goal_scored = False


    # Draw Everything
    pygame.draw.line(screen, WHITE, (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

    pygame.draw.rect(screen, GREEN, left_post)
    pygame.draw.rect(screen, GREEN, right_post)
    pygame.draw.rect(screen, GREEN, left_bar)
    pygame.draw.rect(screen, GREEN, right_bar)

    pygame.draw.circle(screen, BLUE, (int(player_pos[0]), int(player_pos[1])), player_radius)
    pygame.draw.circle(screen, ORANGE, (int(enemy_pos[0]), int(enemy_pos[1])), enemy_radius)
    pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)

    screen.blit(font.render(f"Left: {score_left}", True, WHITE), (50, 30))
    screen.blit(font.render(f"Right: {score_right}", True, WHITE), (WIDTH - 170, 30))

    exit_text = font.render("Press = to Exit Game", True, WHITE)
    screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 10))


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
