import pygame
import math
from config import *

class BotLevel2:
    def __init__(self):
        def load_images(frame_list, resize=(120, 135)):
            loaded_images = []
            for frame in frame_list:
                try:
                    img = pygame.image.load(frame)
                    img = pygame.transform.scale(img, resize)
                    loaded_images.append(img)
                except pygame.error:
                    print(f"Error: Could not load image {frame}")
            return loaded_images

        idle_frames = [f'images/bot_level_2/Idle-{str(i).zfill(2)}.png' for i in range(1, 9)]
        run_frames = [f'images/bot_level_2/Run-{str(i).zfill(2)}.png' for i in range(1, 9)]
        jump_frames = [f'images/bot_level_2/Jump-{str(i).zfill(2)}.png' for i in range(1, 9)]
        attack_frames = [f'images/bot_level_2/Attack-{str(i).zfill(2)}.png' for i in range(1, 3)]
        dead_frames = [f'images/bot_level_2/Dead-{str(i).zfill(2)}.png' for i in range(1, 5)]

        self.idle_animation = load_images(idle_frames)
        self.run_animation = load_images(run_frames)
        self.jump_animation = load_images(jump_frames)
        self.attack_animation = load_images(attack_frames)
        self.dead_animation = load_images(dead_frames)
        
        if not all([self.idle_animation, self.run_animation, self.jump_animation]):
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
        self.position_y = GROUND_Y # initial vertical position
        self.move_speed = 5  # Movement speed
        self.rect = pygame.Rect(
            self.position_x + 50,              # offset_x
            self.position_y - self.jump_height,  # offset_y
            85, 100                            # width, height
        )
        self.is_jumping_over_ball = False
        
        self.is_paused = False  # Flag to check if the bot is paused
        
        self.stationary = False  # Flag to check if the bot is stationary
        
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
                self.jump_speed = max(0, self.jump_speed - 0.2)
                print(f"Jumping: height={self.jump_height:.2f}, speed={self.jump_speed:.2f}")
            else:
                # Apex reached
                self.jump_height = 200
                self.is_jumping = False
                self.jump_speed = 10
                print("Reached jump apex")

        # Fall if not grounded
        if not self.is_grounded:
            if self.jump_height > 0:
                self.jump_height -= self.fall_speed
                self.fall_speed = min(10, self.fall_speed + 0.5 * gravity)
                if self.fall_speed < 0.2:
                    self.fall_speed = 0.2
            else:
                self.jump_height = 0
                self.fall_speed = 0
                self.is_grounded = True
                self.is_jumping = False
                self.is_jumping_over_ball = False
                print("Landed")


        # Ensure the character stays within screen bounds
        self.position_x = max(0, min(WIDTH - 150, self.position_x)) 
        self.position_y = max(0, min(HEIGHT - 200, self.position_y))

        offset_x = 25
        offset_y = 50
        self.rect.x = self.position_x + offset_x
        self.rect.y = self.position_y - self.jump_height + offset_y
        
        # Prevent falling off-screen
        if self.rect.bottom > GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.jump_height = 0
            self.fall_speed = 0
            self.is_grounded = True
            self.is_jumping = False
            self.is_jumping_over_ball = False
                        
        if self.is_grounded and not self.stationary:
            if abs(self.move_speed) > 0 and self.current_action != "run":
                self.current_action = "run"
                self.set_animation()
            elif self.move_speed == 0 and self.current_action != "idle":
                self.current_action = "idle"
                self.set_animation()
        
        if self.stationary:
            if self.current_action != "idle":
                self.current_action = "idle"
                self.set_animation()
    
    def set_animation(self):
        previous_animation = self.current_animation

        if not self.is_grounded:
            self.current_animation = self.jump_animation
        elif self.current_action == "idle":
            self.current_animation = self.idle_animation
        elif self.current_action == "run":
            self.current_animation = self.run_animation
        elif self.current_action == "attack":
            self.current_animation = self.attack_animation
        elif self.current_action == "jump":
            self.current_animation = self.jump_animation
            self.is_jumping = True
            self.is_grounded = False
        elif self.current_action == "dead":
            self.current_animation = self.dead_animation

        # Reset frame index only if animation changed
        if previous_animation != self.current_animation:
            self.frame_index = 0
        
    def draw(self, surface):
        img = self.current_animation[self.frame_index]
        draw_x = self.position_x 
        draw_y = self.position_y - self.jump_height + 20

        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)

        # Draw the character image
        surface.blit(img, (draw_x, draw_y))

        # Draw the bounding rectangle (use same width/height as image)
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
        
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
        self.jump_speed = 10 
        
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
    
    
    def auto_chase(self, ball):
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

            if self.current_action != "attack":
                self.current_action = "attack"
                self.set_animation()
                
        if ball_rect.left > bot_rect.right and self.is_grounded:
            self.position_x += self.move_speed
            self.is_flipped = False

            if self.current_action != "run":
                self.current_action = "run"
                self.set_animation()

        if ball_rect.left == bot_rect.right and ball_rect.bottom > bot_rect.top:    
            self.is_flipped = False
            self.is_jumping_over_ball = True

            if self.current_action != "jump":
                self.current_action = "jump"
                self.set_animation()
    
        # Jump if the ball is above the bot and the bot is on the ground
        if ball_rect.bottom < bot_rect.top and self.is_grounded and abs(ball_rect.centerx - bot_rect.centerx) < 100:
            if self.current_action != "jump":
                self.current_action = "jump"
                self.set_animation()

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


