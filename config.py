import pygame

# Screen
WIDTH, HEIGHT = 800, 600
GROUND_Y = HEIGHT - 50
FPS = 60

# Colors
WHITE = (255, 255, 255)

# Controls
CONTROL_KEYS = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_SPACE}

# Physics
gravity = 0.5

# Total Game Time
TOTAL_TIME = 10  # seconds