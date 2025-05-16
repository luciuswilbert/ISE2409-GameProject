import random
import pygame
import time
import sys
from config import GROUND_Y, TOTAL_TIME, WIDTH
from power_bar import PowerBar
from sound_manager import play_sound
from explosion_effect import ExplosionEffect
from meteor_effect import MeteorEffect
from sound_manager import stop_sound



class Arena:
    def __init__(self, level=1):
        self.explosion_effect = None
        self.enemy_special_active = False
        self.player_dead = False
        self.player_dead_timer = 0
        self.meteor_effect = None
        self.meteor_triggered = False
        self.lucifer_skill_toggle = 0  # 0 for explosion, 1 for meteor
        self.meteor_carrying_ball = False  # Tracks if ball is being carried by meteor
        self.meteor_ball_x = 0
        self.meteor_ball_y = 0
        self.meteor_ball_locked = False

        self.level = level  # Set the level attribute
        # load Background
        if level == 1:
            self.background_img_raw = pygame.image.load("images/background/fire_animatiaon.gif")
        else:
            self.background_img_raw = pygame.image.load("images/background/throne room.png")
        
        self.background_img = pygame.transform.scale(self.background_img_raw, (800, 600))

        self.explosion_frames = []
        for i in range(1, 11):  
            img = pygame.image.load(f"images/effectLevel2/Explosion_{i}.png").convert_alpha()
            self.explosion_frames.append(img)
            print(f"Loaded {len(self.explosion_frames)} explosion frames.")

        
        # Load Goal
        self.football_net_img = pygame.image.load("images/goal/soccer-goal.png")
        self.football_net_img = pygame.transform.scale(self.football_net_img, (100, 300))
        self.left_net_rect = pygame.Rect(0, 300, 100, 250)     # Left side
        self.right_net_rect = pygame.Rect(700, 300, 100, 250)  # Right side
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
            print(" Time's up!")
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
                print(f"DEMON GOAL!  Last touched by demon. Score: Character {self.score}, Demon {self.enemy_score}")
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
                print(f"CHARACTER GOAL!  Last touched by character. Score: Character {self.score}, Demon {self.enemy_score}")
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
        
    def update(self, character, ball):
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

        # Enemy AI for using power
        if (self.enemy_power_bar.is_full and 
            not self.celebrating and 
            not self.enemy_special_active and  
            random.random() < 0.02):

            self.enemy_power_bar.use_power()
            print("Enemy used special power!")

            if self.lucifer_skill_toggle == 0:
                # --- Explosion Skill ---
                play_sound('bomb')
                self.enemy_special_active = True

                player_center = (
                    character.position_x + 75,
                    character.position_y - character.jump_height - 80
                )
                self.explosion_effect = ExplosionEffect(self.explosion_frames, player_center, duration=50)
                self.lucifer_skill_toggle = 1  # Next skill will be meteor

            else:
                # --- Meteor Skill ---
                play_sound('meteor')
                if not self.meteor_triggered:
                    start_pos = (750, 0)
                    end_pos = (50, 500)  # almost bottom center of the goal net
                    self.meteor_effect = MeteorEffect(start_pos, end_pos, duration=50)
                    self.meteor_triggered = True
                    self.meteor_carrying_ball = True  # <--- ADD THIS
                self.lucifer_skill_toggle = 0  # Next skill will be explosion


        
        if self.enemy_special_active and self.explosion_effect:
            self.explosion_effect.update()
            if not self.explosion_effect.active and not self.player_dead:
                stop_sound('bomb')
                self.player_dead = True
                self.player_dead_timer = 120  # 2 seconds at 60 FPS
                print("Player is dead!")

        if self.player_dead:
            self.player_dead_timer -= 1
            if self.player_dead_timer <= 0:
                character.reset()
                self.player_dead = False
                self.enemy_special_active = False
                print("Player respawned!")
        # Update meteor effect
        if self.meteor_effect:
            self.meteor_effect.update()
                # === NEW: Make the ball follow the meteor while it's flying ===
            if self.meteor_carrying_ball:
                t = min(1, self.meteor_effect.counter / self.meteor_effect.duration)
                x = (1 - t) * self.meteor_effect.start_pos[0] + t * self.meteor_effect.end_pos[0]
                y = (1 - t) * self.meteor_effect.start_pos[1] + t * self.meteor_effect.end_pos[1]
                self.meteor_ball_x = int(x)
                self.meteor_ball_y = int(y)
                self.meteor_ball_locked = True

            if not self.meteor_effect.active:
                stop_sound('meteor')
                self.meteor_effect = None
                self.meteor_triggered = False
                if self.meteor_carrying_ball:
                    # Place the ball at meteor's landing spot
                    ball.pos[0] = self.meteor_ball_x
                    ball.pos[1] = self.meteor_ball_y
                    self.meteor_carrying_ball = False
                    self.meteor_ball_locked = False


        





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
        flipped_left_net = pygame.transform.flip(self.football_net_img, True, False)

        screen.blit(self.background_img, (0, 0))
        screen.blit(flipped_left_net, self.left_net_rect.topleft)  # Left net
        screen.blit(self.football_net_img, self.right_net_rect.topleft)  # Right net
        
        self.draw_score(screen)
        self.draw_timer(screen)
        
        # Only draw the ball if the meteor is NOT active
        if not self.meteor_effect:
            ball.draw(screen)
        # (draw meteor effect below as usual)
        if self.meteor_effect:
            self.meteor_effect.draw(screen)
        
        if not self.player_dead:
            character.draw(screen)
        else:
            pass  # (optional: draw a faint marker or nothing)
        bot.draw(screen)

        # Draw the effect on top of the player
        if self.enemy_special_active and self.explosion_effect:
            self.explosion_effect.draw(screen)


        # Draw celebration text
        if self.celebrating:
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

        if self.meteor_effect:
            self.meteor_effect.draw(screen)

        
        return self.win