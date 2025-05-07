import pygame
import sys

from config import *
from ball import Ball
from character import CharacterAnimation
from arena import Arena
from bot import Bot

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Legends of Orbithra")
clock = pygame.time.Clock()

# Game elements (create objects)
ball = Ball()
player = CharacterAnimation()
arena = Arena()
bot = Bot()

character_rects = [player, bot]
goal_rects = [arena.left_net_rect_side_bar, arena.left_net_rect_top_bar, arena.right_net_rect_top_bar, arena.right_net_rect_side_bar]
ball_rect = ball.get_rect()

keys_pressed = set()

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            keys_pressed.add(event.key)
            if event.key == pygame.K_k:
                player.current_action = "kick"
            elif event.key == pygame.K_SPACE and player.is_grounded:
                player.current_action = "jump"
            elif event.key in CONTROL_KEYS.values():
                player.current_action = "run"
            player.set_animation()

        elif event.type == pygame.KEYUP:
            keys_pressed.discard(event.key)
            if not keys_pressed:
                player.current_action = "idle"
                player.set_animation()

    # Update game state for player
    player.update(keys_pressed)
    
    # Update game state for bot
    bot.auto_chase(ball, player)
    bot.update()
    
    # Update game state for ball
    dead_ball = ball.update(goal_rects, character_rects, player, bot) 

    # Update scoreboard
    goal_scored = arena.update_score(ball.get_rect())

    # Draw game elements
    arena.draw(screen, ball, player, bot)
    
    if goal_scored or dead_ball:
        # Reset positions here safely
        ball.reset()
        player.reset()
        bot.reset()

    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()