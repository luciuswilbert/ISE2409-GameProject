import pygame
import sys
from game import Game

# Initialize Pygame
pygame.init()

# Game Constants

def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()


pygame.quit()
sys.exit()
