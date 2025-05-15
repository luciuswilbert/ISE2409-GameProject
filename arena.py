import random
import pygame
import time
from config import *
from power_bar import PowerBar
from sound_manager import play_sound


class Arena:
    def __init__(self, level=1):
        self.level = level  # Set the level attribute
        # load Background
        if level == 1:
            self.background_img_raw = pygame.image.load("images/background/fire_animatiaon.gif")
            self.football_net_img = pygame.image.load("images/goal/lava_goal.png")
            self.football_net_img = pygame.transform.scale(self.football_net_img, (90, 200))
            
            
        else:
            self.background_img_raw = pygame.image.load("images/background/throne room.png")
            self.football_net_img = pygame.image.load("images/goal/soccer-goal.png")
            self.football_net_img = pygame.transform.scale(self.football_net_img, (100, 200))
            
        
        self.background_img = pygame.transform.scale(self.background_img_raw, (800, 600))
        
        # Load Goal
        self.left_net_rect = pygame.Rect(0, 350, 100, 250)     # Left side
        self.right_net_rect = pygame.Rect(720, 350, 100, 250)  # Right side
        self.left_net_rect_goal_area = pygame.Rect(30, 395, 50, 150)
        self.right_net_rect_goal_area = pygame.Rect(720, 395, 50, 150)
        self.left_net_rect_top_bar = pygame.Rect(30, 380, 50, 15)
        self.left_net_rect_side_bar = pygame.Rect(0, 380, 30, 165)
        self.right_net_rect_top_bar = pygame.Rect(720, 380, 50, 15)
        self.right_net_rect_side_bar = pygame.Rect(770, 380, 30, 165)
        
        # Load font and setup timer
        self.start_time = time.time()
        self.total_time = TOTAL_TIME
        self.font = pygame.font.Font(None, 36)
        
        # Initialize score
        self.score = 0
        self.enemy_score = 0 
        self.score_font = pygame.font.Font(None, 48)
        self.celebrating = False
        self.celebration_message = ""
        self.celebration_start_time = None
        self.celebration_duration_sec = 2  # seconds
        self.clock = pygame.time.Clock()
        self.ball_last_kicked_by_character = True
        self.time_out = False
        self.win = False
        self.game_started = False
        
        # Add timer pausing (from first version)
        self.paused = False
        self.pause_start_time = 0
        self.total_paused_time = 0

        # Power bars (from second version) - Pass level to PowerBar
        self.player_power_bar = PowerBar(is_player=True, level=self.level)
        self.enemy_power_bar = PowerBar(is_player=False, level=self.level)
        self.power_cooldown = 5  # seconds

    def pause_timer(self):
        """Pause the game timer"""
        if not self.paused:
            self.paused = True
            self.pause_start_time = time.time()

    def resume_timer(self):
        """Resume the game timer"""
        if self.paused:
            self.paused = False
            self.total_paused_time += time.time() - self.pause_start_time
            # self.player_power_bar.resume()
            # self.enemy_power_bar.resume()

    def draw_timer(self, screen):
        """Draw the game timer with pause support"""
        if self.paused:
            elapsed = int(self.pause_start_time - self.start_time - self.total_paused_time)
        else:
            elapsed = int(time.time() - self.start_time - self.total_paused_time)
        
        remaining = max(0, self.total_time - elapsed)
        timer_surface = self.font.render(f"Time: {remaining}", True, (0, 0, 0))
        timer_rect = timer_surface.get_rect(midtop=(400, 20))
        bg_rect = pygame.Rect(timer_rect.left - 5, timer_rect.top - 5, timer_rect.width + 10, timer_rect.height + 10)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        screen.blit(timer_surface, timer_rect)

        if remaining <= 0 and not self.time_out:
            print("⏰ Time's up!")
            pygame.time.wait(100)
            self.time_out = True
            if self.score > self.enemy_score:
                self.win = True
            elif self.score < self.enemy_score:
                self.win = False
            else:
                self.win = None  # For a draw
            
    def draw_score(self, screen):
        """Draw both player and enemy scores"""
        # Player score (left side)
        score_surface = self.score_font.render(f"Character: {self.score}", True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(20, 20))
        bg_rect = pygame.Rect(score_rect.left - 5, score_rect.top - 5, score_rect.width + 10, score_rect.height + 10)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        screen.blit(score_surface, score_rect)

        # Enemy score (right side)
        enemy_score_surface = self.score_font.render(f"Demon: {self.enemy_score}", True, (0, 0, 0))
        enemy_score_rect = enemy_score_surface.get_rect(topright=(780, 20))
        bg_enemy_rect = pygame.Rect(enemy_score_rect.left - 5, enemy_score_rect.top - 5, enemy_score_rect.width + 10, enemy_score_rect.height + 10)
        pygame.draw.rect(screen, (255, 255, 255), bg_enemy_rect)
        screen.blit(enemy_score_surface, enemy_score_rect)
    
    def update_score(self, ball_rect):
        """Update score based on who last touched the ball"""
        if self.celebrating:
            return False
            
        # Check if ball is close to ground
        is_on_ground = ball_rect.bottom > GROUND_Y - 30
        
        # Enhanced goal detection that includes ground-rolling balls
        left_goal_scored = (self.left_net_rect_goal_area.contains(ball_rect) or 
                        (is_on_ground and ball_rect.centerx < 80 and ball_rect.right > 0))
        
        right_goal_scored = (self.right_net_rect_goal_area.contains(ball_rect) or 
                        (is_on_ground and ball_rect.centerx > 720 and ball_rect.left < WIDTH))
        
        if left_goal_scored and not self.celebrating:
            # Ball went into LEFT goal (CHARACTER's goal)
            
            # Demon scores if they last touched it
            if not self.ball_last_kicked_by_character:
                self.enemy_score += 1
                print(f"DEMON GOAL! 👿 Last touched by demon. Score: Character {self.score}, Demon {self.enemy_score}")
                self.celebrating = True
                self.celebration_message = "DEMON Goal"
                self.celebration_start_time = time.time()
                
                # Always play sound regardless of celebration state - use dedicated channel
                try:
                    pygame.mixer.Channel(1).play(pygame.mixer.Sound('sounds/goal_enemy.mp3'))
                except:
                    # Fallback to function if direct channel fails
                    play_sound('goal_enemy')
                
                return True
            else:
                # Character put ball in own goal - no score
                print("Character own goal - no score, just reset")
                
                # Always play whistle sound - use dedicated channel
                try:
                    pygame.mixer.Channel(2).play(pygame.mixer.Sound('sounds/whistle.mp3'))
                except:
                    # Fallback to function if direct channel fails
                    play_sound('whistle')
                
                return True
                
        elif right_goal_scored and not self.celebrating:
            # Ball went into RIGHT goal (DEMON's goal)
            
            # Character scores if they last touched it
            if self.ball_last_kicked_by_character:
                self.score += 1
                print(f"CHARACTER GOAL! 🎯 Last touched by character. Score: Character {self.score}, Demon {self.enemy_score}")
                self.celebrating = True
                self.celebration_message = "Goal!"
                self.celebration_start_time = time.time()
                
                # Always play sound regardless of celebration state - use dedicated channel
                try:
                    pygame.mixer.Channel(3).play(pygame.mixer.Sound('sounds/goal_player.mp3'))
                except:
                    # Fallback to function if direct channel fails
                    play_sound('goal_player')
                
                return True
            else:
                # Demon put ball in own goal - no score
                print("Demon own goal - no score, just reset")
                
                # Always play whistle sound - use dedicated channel
                try:
                    pygame.mixer.Channel(4).play(pygame.mixer.Sound('sounds/whistle.mp3'))
                except:
                    # Fallback to function if direct channel fails
                    play_sound('whistle')
                
                return True
                
        return False
        
    def update(self, bot):
        """Update game state including celebrations and power bars"""
        if self.celebrating:
            current_time = time.time()
            elapsed = current_time - self.celebration_start_time
            
            if elapsed >= self.celebration_duration_sec:
                print("Celebration ended!")
                self.celebrating = False
                
        # Update power bars
        self.player_power_bar.update()
        self.enemy_power_bar.update()
            
        if (self.enemy_power_bar.is_full and not self.celebrating and bot.current_action == "kick" and random.random() < 0.5):  # 2% chance per frame
            self.enemy_power_bar.use_power()
            
            if random.random() < 0.5:
                bot.start_power_kick()
                print("Enemy used special power: Power Kick!")
            else:
                bot.start_ground_fire()
                print("Enemy used special power: Ground Fire!")


    def draw_hint(self, screen, hint_text):
        """Draw the hint text for powers"""
        if self.font:
            # Create the surface for the hint text
            hint_surface = self.font.render(hint_text, True, (255, 255, 255))
            hint_rect = hint_surface.get_rect(midtop=(400, 550))  # Adjust position as needed

            # Draw background for better readability
            bg_rect = pygame.Rect(hint_rect.left - 5, hint_rect.top - 5, hint_rect.width + 10, hint_rect.height + 10)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            
            # Draw the hint text on the screen
            screen.blit(hint_surface, hint_rect)


    def draw(self, screen, ball, character, bot):
        """Draw all arena elements"""
        flipped_right_net = pygame.transform.flip(self.football_net_img, True, False)

        screen.blit(self.background_img, (0, 0))
        
        bot.trigger_full_ground_fire(screen, character)
        bot.trigger_power_kick(ball, screen)
        
        screen.blit(flipped_right_net, self.right_net_rect.topleft)  # Left net
        screen.blit(self.football_net_img, self.left_net_rect.topleft)  # Right net
        
        self.draw_score(screen)
        # pygame.draw.rect(screen, (255, 0, 0), self.left_net_rect, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.right_net_rect, 2)
        
        # # Draw first rectangle (e.g., red, filled)
        # pygame.draw.rect(screen, (255, 0, 0), self.left_net_rect_top_bar, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.left_net_rect_side_bar, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.right_net_rect_top_bar, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.right_net_rect_side_bar, 2)

        # # # Draw second rectangle (e.g., green, outlined)
        # pygame.draw.rect(screen, (0, 255, 0), self.left_net_rect_goal_area, 2)
        # pygame.draw.rect(screen, (0, 255, 0), self.right_net_rect_goal_area, 2)
    
        self.draw_timer(screen)
        
        ball.draw(screen)
        character.draw(screen)
        bot.draw(screen)

        # Draw celebration text
        if self.celebrating:
            print("Celebration in progress!")
            font = pygame.font.SysFont(None, 100)
            goal_text = font.render(self.celebration_message, True, (255, 215, 0))  # Gold text
            screen.blit(goal_text, (400 - goal_text.get_width() // 2, 250))

        # Show result if time is up
        if self.time_out:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(180)
            overlay.fill((128, 128, 128))  # Gray
            screen.blit(overlay, (0, 0))

            result_font = pygame.font.SysFont(None, 100)
            if self.win is True:
                result_text = result_font.render("You Win!", True, (0, 255, 0))
            elif self.win is False:
                result_text = result_font.render("You Lose!", True, (255, 0, 0))
            else:
                result_text = result_font.render("Draw!", True, (255, 255, 0))

            screen.blit(result_text, (400 - result_text.get_width() // 2, 250))
        
        # Draw power bars
        self.player_power_bar.draw(screen)
        self.enemy_power_bar.draw(screen)
        
        # Note: Bottom screen hint has been removed
        # Hints are now only shown when the power bar is full
        
        return self.win
        
    def apply_blur_effect_with_dark_top(self, screen):
        # Step 1: Apply Blur
        scale = 0.1  # Lower = more blur
        small_size = (int(WIDTH * scale), int(HEIGHT * scale))
        small_surface = pygame.transform.smoothscale(screen, small_size)
        blurred_surface = pygame.transform.smoothscale(small_surface, (WIDTH, HEIGHT))
        blurred_surface.set_alpha(128)
        screen.blit(blurred_surface, (0, 0))

        # Step 2: Create black-to-transparent gradient (top dark, bottom clear)
        gradient = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(HEIGHT):
            alpha = int(150 * (1 - y / HEIGHT))  # Max alpha at top, 0 at bottom
            color = (0, 0, 0, alpha)
            pygame.draw.line(gradient, color, (0, y), (WIDTH, y))

        # Step 3: Overlay the dark gradient
        screen.blit(gradient, (0, 0))