import pygame
import sys

from config import *

# Initialize Pygame
pygame.init()

#Assets
backgroundImg = pygame.image.load(r"C:\Users\xiuzh\OneDrive - Asia Pacific University\Degree Y2S2\ISE\Assingment\fire_animatiaon.gif")
# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Simple Soccer Game")
clock = pygame.time.Clock()

# Game elements (create objects)


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
    
    
    # Handle collisions after all positions are updated


    # Update scoreboard
    

    # Draw goal post


    # Draw game elements


    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
