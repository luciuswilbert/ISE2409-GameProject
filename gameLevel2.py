import pygame
from config import *
from ball import Ball
from character import CharacterAnimation
from arena import Arena
from bot import Bot
from power_manager import PowerManager
import sys
import time
from sound_manager import play_background_music, play_sound


def GameLevel2(screen):
    # Game elements (create objects)
    play_background_music('background')
    clock = pygame.time.Clock()
    ball = Ball()
    arena = Arena(level=2)  # IMPORTANT: Set level=2 here!
    bot = Bot()
    player = CharacterAnimation()
    
    # Debug: Verify level is set correctly
    print(f"DEBUG: Arena level is set to: {arena.level}")
    
    # Link ball and arena for tracking who kicked last
    ball.arena = arena
    
    # Create power manager using arena's power bar
    power_manager = PowerManager(player, ball, arena, bot, arena.player_power_bar)

    # Define edge rectangles for collision detection
    character_rects = [player, bot]
    goal_rects = [arena.left_net_rect_side_bar, arena.left_net_rect_top_bar, 
                  arena.right_net_rect_top_bar, arena.right_net_rect_side_bar]

    keys_pressed = set()
    goal_cooldown = False
    reset_timer = 0
    RESET_DELAY = 60  # frames to wait after goal before reset

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and not arena.celebrating:
                keys_pressed.add(event.key)
                
                # Handle power shot with 'p' key using power manager
                if event.key == pygame.K_p and not power_manager.is_power_active:
                    if power_manager.activate_power():
                        # Power activated successfully, don't process other animations
                        continue

                # Handle vine power - Available in Level 2
                if event.key == pygame.K_v and not power_manager.is_vine_active:
                    if power_manager.activate_vine():
                        # Play vine activation sound
                        play_sound('vine_power')
                        continue

                # Only process normal animations if not in power mode
                if not power_manager.is_power_active:
                    if event.key == pygame.K_k:
                        player.current_action = "kick"
                        play_sound('ball_kick')
                    elif event.key == pygame.K_SPACE and player.is_grounded:
                        player.current_action = "jump"
                    elif event.key in CONTROL_KEYS.values():
                        player.current_action = "run"
                    player.set_animation()

            elif event.type == pygame.KEYUP and not arena.celebrating:
                keys_pressed.discard(event.key)
                # Only change to idle if not in power mode and no keys pressed
                if not keys_pressed and not power_manager.is_power_active:
                    player.current_action = "idle"
                    player.set_animation()

        # Update arena (handles its own celebrations and power bars)
        arena.update()
        
        # Handle celebration and reset timing
        if arena.celebrating:
            # During celebration, count frames
            reset_timer += 1
            
            # Clear any pressed keys during celebration
            if keys_pressed:
                keys_pressed.clear()
            
            # Check if celebration duration has passed
            current_time = time.time()
            if current_time - arena.celebration_start_time >= arena.celebration_duration_sec:
                # Start reset phase
                arena.celebrating = False
                print("Celebration ended, starting reset phase")
        elif goal_cooldown and reset_timer > 0:
            # Post-celebration reset phase
            reset_timer += 1
            if reset_timer >= RESET_DELAY:
                print("Resetting game after goal")
                
                # Reset ball using its own reset method
                ball.reset()  # This will put it back to [WIDTH//2, 100]
                
                # Reset players
                player.reset()
                bot.is_paused = False
                bot.reset()
                
                # Reset power manager
                power_manager.reset()
                
                # Resume timer and clear cooldown
                arena.resume_timer()
                goal_cooldown = False
                reset_timer = 0
                
                print(f"Ball reset to default sky position: ({ball.pos[0]}, {ball.pos[1]})")
        else:
            # Normal game logic (not celebrating)
            # Update power manager (handles both powers)
            power_manager.update(keys_pressed)
            
            # Update game state for player (normal physics only if not in power mode)
            if not power_manager.is_power_active:
                player.update(keys_pressed)
            
            # Update game state for bot
            bot.auto_chase(ball, player)
            bot.update()
            
            # UPDATED: Check vine collision before updating ball
            # Now correctly handles a list of vine rectangles
            vine_rects = power_manager.get_vine_rect()
            if vine_rects:
                # Debug: Print the vine rects before passing to ball
                ball.check_vine_collision(vine_rects)
            
            # Update game state for ball
            dead_ball = ball.update(goal_rects, character_rects, player, bot) 

            # Update scoreboard
            ball_rect = ball.get_rect()
            
            # Check if ball is in goal area
            in_goal_area = (arena.left_net_rect_goal_area.colliderect(ball_rect) or 
                           arena.right_net_rect_goal_area.colliderect(ball_rect))
            
            # Clear goal cooldown if ball leaves goal areas
            if not in_goal_area and not goal_cooldown:
                goal_cooldown = False
            
            # Check for goal scored ONLY if not in cooldown
            if not goal_cooldown:
                goal_scored = arena.update_score(ball_rect)
                
                # When something happened in goal area (score or own goal attempt)
                if goal_scored:
                    print("Goal detected, starting celebration/reset sequence")
                    goal_cooldown = True
                    reset_timer = 1  # Start counting for reset
                    
                    # Turn off special effects immediately
                    ball.special_effect_active = False
                    ball.previous_positions = []
                    ball.particles = []
                    
                    # End power mode if active
                    if power_manager.is_power_active:
                        power_manager._end_power_mode()
                    
                    # Force bot to be visible and in a consistent position
                    # IMPORTANT: This is critical for maintaining visibility during celebration
                    bot.is_paused = False
                    bot.position_x = 570  # Fixed position X
                    bot.position_y = GROUND_Y - 150  # Place slightly higher to ensure visibility
                    bot.jump_height = 0  # Reset any jumping
                    bot.is_jumping = False
                    bot.is_grounded = True
                    bot.current_action = "idle"
                    bot.current_animation = bot.idle_animation
                    bot.frame_index = 0
                    bot.is_flipped = True
                    
                    # Update rectangle
                    bot.rect.x = bot.position_x
                    bot.rect.y = bot.position_y - bot.jump_height + 50
                    
                    # Print bot position for debugging
                    print(f"After goal, bot positioned at: ({bot.position_x}, {bot.position_y})")
                    
                    # Pause timer for celebrations only
                    if arena.celebrating:
                        arena.pause_timer()
                    else:
                        # For own goals, skip celebration and go straight to reset
                        print("Own goal detected, preparing immediate reset")
                        arena.pause_timer()  # Still pause timer briefly
                        play_sound('whistle')
                    
                    # Clear keys
                    keys_pressed.clear()
            
            # Handle dead ball
            if dead_ball and not arena.celebrating and not goal_cooldown:
                print("Dead ball detected, resetting")
                
                # Reset ball using its own reset method
                ball.reset()  # This will put it back to [WIDTH//2, 100]
                
                # Reset players
                player.reset()
                if bot.is_paused:
                    bot.resume()
                bot.reset()
                
                # Reset powers
                power_manager.reset()

        # Draw game elements
        arena.draw(screen, ball, player, bot)
        
        # Draw power effects
        power_manager.draw_power_effects(screen)
        
        # Update display ONCE per frame
        pygame.display.flip()
        clock.tick(FPS)
        
        # Check if game should end
        if arena.time_out:
            print("Level 2 Game Over!")
            running = False
      
    # Check if player has won
    if arena.win is True:
        print("Player wins Level 2!")
        return True
    elif arena.win is False:
        print("Player loses Level 2!")
        return False
    else:
        print("Draw!")
        return False
