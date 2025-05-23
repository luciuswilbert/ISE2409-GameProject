from gameLevel1 import GameLevel1
from gameLevel2 import GameLevel2
import pygame
from sound_manager import initialize_sounds
from config import WIDTH, HEIGHT


# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Initialize sounds
initialize_sounds()

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        
        
GameLevel1(screen)        

GameLevel2(screen)