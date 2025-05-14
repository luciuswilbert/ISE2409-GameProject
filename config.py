import pygame

# Screen
WIDTH, HEIGHT = 800, 600
GROUND_Y = HEIGHT - 50
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)

# Controls
CONTROL_KEYS = {"left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_SPACE}

# Physics
gravity = 0.5

# Total Game Time
TOTAL_TIME = 60  # seconds

# Debug settings
DEBUG_MODE = False  # Set to True to enable collision visualization