import pygame
import sys

from config import *
from ball import Ball

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Simple Soccer Game")
clock = pygame.time.Clock()

# Game elements (create objects)
ball = Ball();

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    # Get player inputs
    keys = pygame.key.get_pressed()
    
    # Player handle input


    # Update game state for player
    
    
    # Update game state for bot
    
    
    # Update game state for ball
    ball.update()  # Pass an empty list for goal_rects since we don't have any goals yet
    
    # Handle collisions after all positions are updated


    # Update scoreboard
    

    # Draw goal post


    # Draw game elements
    ball.draw(screen)

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
