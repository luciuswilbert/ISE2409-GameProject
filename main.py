import pygame
import sys

from config import *
from gameLevel1 import GameLevel1
from gameLevel2 import GameLevel2
from storyscene.introscene1 import *

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Legends of Orbithra")
    
# Start menu and story intro
# play_first_video(screen)
play_intro_scene(screen)

# Game level 1
while True:    
    if GameLevel1(screen):        
        break # If player wins level 1, break the loop to transition to level 2
    else:
        # If player loses level 1, show restart menu
        # If player chooses NOT to restart level 1, quit the game
        pygame.quit()
        sys.exit()      

# Transition to level 2


# Game level 2
while True:    
    if GameLevel2(screen):        
        break # If player wins level 2, break the loop to transition to story outro
    else:
        # If player loses level 2, show restart menu
        # If player chooses NOT to restart level 2, quit the game
        pygame.quit()
        sys.exit()  
    

# Story outro


pygame.quit()
sys.exit()