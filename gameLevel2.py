import pygame
from config import *
from ball import Ball
from character import CharacterAnimation
from arena import Arena
from botLevel2 import BotLevel2
import sys

def GameLevel2(screen):
   
    # Game elements (create objects)
    clock = pygame.time.Clock()
    ball = Ball()
    player = CharacterAnimation()
    arena = Arena(2)
    bot = BotLevel2()

    # Define edge rectangles for collision detection
    character_rects = [player, bot]
    goal_rects = [arena.left_net_rect_side_bar, arena.left_net_rect_top_bar, arena.right_net_rect_top_bar, arena.right_net_rect_side_bar]

    keys_pressed = set()
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
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
        player.update(keys_pressed, bot)
        
        # Update game state for bot
        bot.auto_chase(ball)
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
        
        if arena.time_out:
            print("Level 1 Game Over!")
            running = False
      
    # Check if player has won  
    if arena.win:
        print("Player wins Level 1!")
        return True
    else:
        print("Player loses Level 1!")
        return False