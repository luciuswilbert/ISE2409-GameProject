
import pygame
from config import *
import random
from smokeParticle import SmokeParticle
import pygame.mixer
import pygame.image
import math

class BotLevel1:
    def __init__(self):
        def load_images(frame_list, resize=(110, 110)):
            loaded_images = []
            for frame in frame_list:
                try:
                    img = pygame.image.load(frame)
                    img = pygame.transform.scale(img, resize)
                    loaded_images.append(img)
                except pygame.error:
                    print(f"Error: Could not load image {frame}")
            return loaded_images

        idle_frames = [f'images/bot_level_1/Idle A-{str(i).zfill(2)}.png' for i in range(1, 7)]
        run_frames = [f'images/bot_level_1/Run A-{str(i).zfill(2)}.png' for i in range(1, 8)]
        kick_frames = ['images/bot_level_1/Attack A-03.png', 'images/bot_level_1/Attack A-04.png' ]
        jump_frames = [f'images/bot_level_1/Idle A-{str(i).zfill(2)}.png' for i in range(1, 7)]

        self.idle_animation = load_images(idle_frames)
        self.run_animation = load_images(run_frames)
        self.kick_animation = load_images(kick_frames)
        self.jump_animation = load_images(jump_frames)

        if not all([self.idle_animation, self.run_animation, self.kick_animation, self.jump_animation]):
            raise RuntimeError("One or more animations failed to load. Check file paths.")
        
        self.current_animation = self.idle_animation
        self.current_action = "idle"
        self.frame_index = 0
        self.frame_counter = 0
        self.frame_delay = 5
        self.is_jumping = False
        self.is_grounded = True
        self.jump_height = 0
        self.jump_speed = 10
        self.fall_speed = 0
        self.is_flipped = True  # Track direction
        self.position_x = 570  # Initial x position
        self.position_y = GROUND_Y  # initial vertical position
        self.move_speed = 5  # Movement speed
        self.rect = pygame.Rect(
            self.position_x + 50,              # offset_x
            self.position_y - self.jump_height + 50,  # offset_y
            65, 100                            # width, height
        )
        self.is_jumping_over_ball = False
        self.power_kick_particles = []
        self.particles = []
        self.start_fire = False
        self.fire_start_time = None
        self.fire_duration = 3000 
        self.fire_frame_counter = 0
        self.fire_frame_delay = 5  # Adjust this to control particle spawn rate
        self.fire_sound = pygame.mixer.Sound("audio/mixkit-fire-spell-with-explosion-1338.wav")
        self.fire_sound_continuous = pygame.mixer.Sound("audio/fire-noise-159659.mp3")
        self.power_kick = False
        
        # Add paused state
        self.is_paused = False
        
        # Visual effect for frozen state
        self.freeze_effect_timer = 0
        
        # Default draw offset when not paused
        self.default_draw_offset_y = 50
        
        # Draw offset when paused - change this to control position when frozen
        # A value of -100 will place the bot 100px higher than normal
        self.paused_draw_offset_y = 0
        
        print(f"Bot initialized at position ({self.position_x}, {self.position_y}), Paused: {self.is_paused}")

    def update(self):
        # Store last action
        self.last_action = self.current_action
        
        # Skip updates if paused
        if self.is_paused:
            # Still update the freeze effect timer
            self.freeze_effect_timer += 1
            return
            
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)

        if self.is_jumping:
            if self.jump_height < 200:
                self.jump_height += self.jump_speed
                if self.jump_speed > 0:
                    self.jump_speed -= 0.2
                if self.is_jumping_over_ball:
                    self.position_x += self.move_speed
            else:
                self.is_jumping = False
                self.jump_speed = 10
        else:
            if self.jump_height > 0:
                self.jump_height -= self.fall_speed
                if self.fall_speed < 10:
                    self.fall_speed += 0.5 * gravity
                if self.is_jumping_over_ball:
                    self.position_x += self.move_speed
            else:
                self.jump_height = 0
                self.is_grounded = True
                self.fall_speed = 0
                self.is_jumping_over_ball = False

        # Ensure the character stays within screen bounds
        self.position_x = max(0, min(WIDTH - 150, self.position_x)) 
        self.position_y = max(0, min(HEIGHT - 200, self.position_y))

        offset_x = 25
        offset_y = 50
        self.rect.x = self.position_x + offset_x
        self.rect.y = self.position_y - self.jump_height + offset_y

    def set_animation(self):
        if self.current_action == "idle":
            self.current_animation = self.idle_animation
        elif self.current_action == "run":
            self.current_animation = self.run_animation
        elif self.current_action == "kick":
            self.current_animation = self.kick_animation
        elif self.current_action == "jump" and self.is_grounded:
            self.current_animation = self.jump_animation
            self.is_jumping = True
            self.is_grounded = False
        self.frame_index = 0
        
    # def draw(self, surface):
    #     img = self.current_animation[self.frame_index]
    #     draw_x = self.position_x 
    #     draw_y = self.position_y - self.jump_height + 50

    #     if self.is_flipped:
    #         img = pygame.transform.flip(img, True, False)

    #     # Draw the character image
    #     surface.blit(img, (draw_x, draw_y))

    #     # Draw the bounding rectangle (use same width/height as image)
    #     # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
    
    def draw(self, surface):
        # Safety check for animation
        if not self.current_animation or len(self.current_animation) == 0:
            return
            
        if self.frame_index >= len(self.current_animation):
            self.frame_index = 0
            
        # Get current image    
        img = self.current_animation[self.frame_index]
        if img is None:
            return
            
        # Calculate draw position
        draw_x = self.position_x 
        
        # Use different vertical offsets based on paused state
        if self.is_paused:
            # When paused, draw higher on screen while keeping logical position
            draw_y = self.position_y - self.jump_height + self.default_draw_offset_y + self.paused_draw_offset_y
        else:
            # Normal drawing with default offset
            draw_y = self.position_y - self.jump_height + self.default_draw_offset_y

        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)

        # Draw the character image
        surface.blit(img, (draw_x, draw_y))
        
        # Draw collision box if debug mode is enabled
        if DEBUG_MODE:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)  # Red outline
            font = pygame.font.Font(None, 20)
            text = font.render("Bot Hitbox", True, (255, 0, 0))
            surface.blit(text, (self.rect.x, self.rect.y - 20))
            
            # Show action state
            state_text = font.render(f"Action: {self.current_action}", True, (255, 0, 0))
            surface.blit(state_text, (self.rect.x, self.rect.y - 40))
            
            # Show position info
            pos_text = font.render(f"Pos: ({self.position_x}, {self.position_y})", True, (255, 0, 0))
            surface.blit(pos_text, (self.rect.x, self.rect.y - 60))
        
        # When paused, add visual effects
        if self.is_paused:
            # Draw a pulsing outline
            outline_thickness = 3 + int(math.sin(self.freeze_effect_timer * 0.1) * 2)
            outline_color = (0, 191, 255)  # Deep sky blue
            pygame.draw.rect(surface, outline_color, 
                        pygame.Rect(draw_x - 2, draw_y - 2, 
                                    img.get_width() + 4, img.get_height() + 4), 
                        outline_thickness)
            
            # Draw "FROZEN" text with a gentle bounce effect
            font = pygame.font.Font(None, 36)
            text_y_offset = int(math.sin(self.freeze_effect_timer * 0.1) * 3)
            text_surface = font.render("FROZEN", True, (0, 191, 255))
            text_rect = text_surface.get_rect(center=(draw_x + img.get_width() // 2, 
                                                    draw_y - 20 + text_y_offset))
            
            # Draw a semi-transparent background for better visibility
            bg_rect = pygame.Rect(text_rect.left - 5, text_rect.top - 5, 
                                text_rect.width + 10, text_rect.height + 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 128))  # Semi-transparent black
            surface.blit(bg_surface, (bg_rect.left, bg_rect.top))
            
            # Draw text
            surface.blit(text_surface, text_rect)
            
            # Draw icicles hanging from bot (optional visual effect)
            for i in range(3):
                icicle_x = draw_x + img.get_width() * (i + 1) / 4
                icicle_height = 10 + int(math.sin(self.freeze_effect_timer * 0.1 + i) * 3)
                pygame.draw.polygon(surface, (200, 240, 255),  # Light blue
                                [(icicle_x - 3, draw_y + img.get_height()),
                                (icicle_x + 3, draw_y + img.get_height()),
                                (icicle_x, draw_y + img.get_height() + icicle_height)])
        
    # def reset(self):
    #     self.__init__()
    
    def reset(self):
        # Reset position to default starting point
        self.position_x = 570  # Default X position
        self.position_y = GROUND_Y  # Default Y position (should be 550 based on your config)
        
        # Reset jump state
        self.is_jumping = False
        self.is_jumping_over_ball = False
        self.jump_height = 0
        self.is_grounded = True
        self.fall_speed = 0
        
        # Reset animation to idle and face left
        self.current_action = "idle"
        self.current_animation = self.idle_animation
        self.frame_index = 0
        self.is_flipped = True
        
        # Update the collision rectangle
        offset_x = 25
        offset_y = 50
        self.rect.x = self.position_x + offset_x
        self.rect.y = self.position_y - self.jump_height + offset_y
        
        # Reset freeze effect timer
        self.freeze_effect_timer = 0
        
        # Ensure bot is not paused after reset
        self.is_paused = False
        
        self.power_kick = False
 
 
    def auto_chase(self, ball, bot_power_bar):
        # Skip chase logic if paused
        if self.is_paused:
            return
        
        bot_rect = self.rect
        ball_rect = ball.get_rect()

        if ball_rect.right < bot_rect.left:
            self.position_x -= self.move_speed
            self.is_flipped = True

            if self.current_action != "run":
                self.current_action = "run"
                self.set_animation()

        if ball_rect.right == bot_rect.left and ball_rect.bottom > bot_rect.top:
            self.position_x -= self.move_speed
            self.is_flipped = True

            if self.current_action != "kick":
                self.current_action = "kick"
                self.set_animation()
                
        if ball_rect.left > bot_rect.right and self.is_grounded:
            self.position_x += self.move_speed
            self.is_flipped = False

            if self.current_action != "run":
                self.current_action = "run"
                self.set_animation()

        if ball_rect.left == bot_rect.right and ball_rect.bottom > bot_rect.top:    
            self.is_flipped = False
            self.is_jumping = True
            self.is_jumping_over_ball = True

            if self.current_action != "jump":
                self.current_action = "jump"
                self.set_animation()
    
        # Jump if the ball is above the bot and the bot is on the ground
        if ball_rect.bottom - 10 < bot_rect.top and self.is_grounded and abs(ball_rect.centerx - bot_rect.centerx) < 50:
            self.is_jumping = True
            if self.current_action != "jump":
                self.current_action = "jump"
                self.set_animation()
                    
    def trigger_full_ground_fire(self, screen, player):
 
        current_time = pygame.time.get_ticks()

        if self.start_fire:
            if self.fire_start_time is None:
                self.fire_start_time = current_time
                self.fire_sound.play(-1)  # Loop fire sound
                self.fire_sound_continuous.play(-1)  # Loop fire sound continuously

            elapsed = current_time - self.fire_start_time
            remaining = max(self.fire_duration - elapsed, 0)

            if elapsed >= self.fire_duration:
                self.start_fire = False
                self.fire_start_time = None
                self.fire_sound.fadeout(1000)  # Fade out sound after fire ends
                self.fire_sound_continuous.fadeout(1000)  # Fade out sound after fire ends
            else:
                self.fire_frame_counter += 1
                if self.fire_frame_counter >= self.fire_frame_delay:
                    self.fire_frame_counter = 0

                    spawn_factor = remaining / self.fire_duration
                    num_particles_per_column = int(2 * spawn_factor)

                    # if len(self.particles) < self.MAX_PARTICLES and num_particles_per_column > 0:
                    if num_particles_per_column > 0:
                        base_y = HEIGHT
                        step = 5
                        for x in range(0, WIDTH, step):
                            for i in range(num_particles_per_column):
                                flame_color = random.choice([(255, 100, 0), (255, 150, 50), (255, 200, 100)])
                                self.particles.append(SmokeParticle(x + random.randint(-5, 5), base_y, flame_color, "flame"))
             
            # if self.start_fire:          
            #     if player.current_action != "dead": 
            #         if player.current_action == "jump":
            #             print("Jumping")
            #             if player.is_grounded and player.jump_height == 0  and not player.is_jumping:
            #                 player.current_action = "dead"
            #             else:
            #                 player.pending_death = True  # Wait to die when landed
            #         else:
            #             player.current_action = "dead"
            #         player.set_animation(self)                    
            #     player.update({}, self)

            #     # Always update & draw particles
            #     for p in self.particles[:]:
            #         p.update()
            #         p.draw(screen)
            #         if p.life <= 0:
            #             self.particles.remove(p)
            # else:
            #     if player.current_action != "idle":
            #         player.current_action = "idle"
            #         player.set_animation(self)
            #     player.update({}, self)
            
            if self.start_fire:          
                if player.current_action != "dead": 
                    if player.current_action == "jump":
                        print("Jumping")
                        
                        # Wait until grounded before transitioning to dead
                        if player.is_grounded and player.jump_height == 0 and not player.is_jumping:
                            player.current_action = "dead"  # Transition to dead when grounded
                        else:
                            player.pending_death = True  # Set pending death if not grounded yet
                    else:
                        player.current_action = "dead"  # If not jumping, immediately transition to dead
                    
                    player.set_animation(self)                    
                player.update({}, self)

                # Always update & draw particles
                for p in self.particles[:]:
                    p.update()
                    p.draw(screen)
                    if p.life <= 0:
                        self.particles.remove(p)
            else:
                if player.current_action != "idle":
                    player.current_action = "idle"
                    player.set_animation(self)
                player.update({}, self)


    def start_ground_fire(self):
        self.start_fire = True
        self.fire_start_time = None  # Reset the timer   
        
    def trigger_power_kick(self, ball, screen):
        if self.power_kick:
            ball_rect = ball.get_rect()

            # Generate 5–10 new particles (reduce for better performance)
            for _ in range(random.randint(5, 10)):
                self.power_kick_particles.append({
                    'position': [ball_rect.centerx, ball_rect.centery],
                    'velocity': [random.uniform(-3, 3), random.uniform(-5, -1)],
                    'lifetime': 30,
                    'max_lifetime': 30  # Used to calculate color and size fade
                })

        # Update and draw each particle
        for p in self.power_kick_particles[:]:
            # Update position
            p['position'][0] += p['velocity'][0]
            p['position'][1] += p['velocity'][1]
            p['velocity'][1] += 0.1  # gravity
            p['lifetime'] -= 1

            # Calculate color (fade from yellow to red)
            progress = p['lifetime'] / p['max_lifetime']
            r = int(255)
            g = int(140 * progress)  # From 140 → 0
            b = int(0)
            color = (r, g, b)

            # Calculate size (shrink over time)
            radius = max(1, int(6 * progress))

            # Draw with flicker
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 1)
            pygame.draw.circle(screen, color, (int(p['position'][0] + offset_x), int(p['position'][1] + offset_y)), radius)

            # Remove dead particles
            if p['lifetime'] <= 0:
                self.power_kick_particles.remove(p)

    def start_power_kick(self):
        self.power_kick = True

       
    def pause(self):
        """Pause the bot's movement but keep it visually present on the ground"""
        # Set the pause flag
        self.is_paused = True
        
        # Force bot to be on the ground - keep x position but reset y position
        self.jump_height = 0
        self.is_jumping = False
        self.is_grounded = True
        self.fall_speed = 0
        
        # Reset animation to idle and face left
        self.current_action = "idle"
        self.current_animation = self.idle_animation
        self.frame_index = 0
        self.is_flipped = True
        
        # Update rect position to match new ground position
        offset_x = 25
        offset_y = 50
        self.rect.x = self.position_x + offset_x
        self.rect.y = self.position_y - self.jump_height + offset_y
        
        # Reset freeze effect timer for visual effects
        self.freeze_effect_timer = 0
        
        print(f"Bot paused at x={self.position_x}, on ground")
        
    def resume(self):
        """Resume the bot's movement with proper state restoration"""
        # Reset the paused flag
        self.is_paused = False
        
        # Reset key movement flags
        self.is_jumping_over_ball = False  # If you have this flag
        
        # Make sure the bot is in a valid state for movement
        if not self.is_jumping:
            self.is_grounded = True
        
        # Reset to idle animation if not already in an action
        if self.current_action == "idle":
            self.current_animation = self.idle_animation
            self.frame_index = 0
        
        # Clear any special states or timers
        self.freeze_effect_timer = 0
        
        print(f"Bot resumed at position ({self.position_x}, {self.position_y})")
