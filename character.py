import pygame
from config import *
import time

class CharacterAnimation:
    def __init__(self):
        def load_images(frame_list, resize=(150, 200)):
            loaded_images = []
            for frame in frame_list:
                try:
                    img = pygame.image.load(frame)
                    img = pygame.transform.scale(img, resize)
                    loaded_images.append(img)
                except pygame.error:
                    print(f" Error: Could not load image {frame}")
            return loaded_images

        idle_frames = [f'images/player/Idle A-{str(i).zfill(2)}.png' for i in range(1, 7)]
        run_frames = [f'images/player/Run A-{str(i).zfill(2)}.png' for i in range(1, 9)]
        kick_frames = ['images/player/Attack A-03.png', 'images/player/Attack A-04.png']
        jump_frames = [f'images/player/Jump A-{str(i).zfill(2)}.png' for i in range(1, 11)]
        dead_frames = [f'images/player/Dead-{str(i).zfill(2)}.png' for i in range(1, 4)]
        hurt_frames = [f'images/player/Hurt-{str(i).zfill(2)}.png' for i in range(1, 4)]

        self.idle_animation = load_images(idle_frames)
        self.run_animation = load_images(run_frames)
        self.kick_animation = load_images(kick_frames)
        self.jump_animation = load_images(jump_frames)
        self.dead_animation = load_images(dead_frames)
        self.hurt_animation = load_images(hurt_frames)

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
        self.is_flipped = False
        self.position_x = 100
        self.position_y = GROUND_Y
        self.move_speed = 5
        self.rect = pygame.Rect(
            self.position_x + 40,
            self.position_y - self.jump_height + 40,
            60, 100
        )
        self.is_dying = False
        self.power_kick_hit = False
        self.pending_death = False
        
    # def update(self, keys_pressed):
    #     # Update animation frame
    #         self.position_x + 50,              # offset_x
    #         self.position_y - self.jump_height + 50,  # offset_y
    #         65, 100                            # width, height


    def draw_score(self):
        score_surface = self.score_font.render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(20, 20))
        bg_rect = pygame.Rect(score_rect.left - 5, score_rect.top - 5, score_rect.width + 10, score_rect.height + 10)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        self.screen.blit(score_surface, score_rect)

    def update(self,keys_pressed,bot=None):
        # Stop all movement & physics if dead, but allow animation to progress
        if self.is_dying:
            if not self.is_grounded:
                # Simulate falling down during death
                if self.jump_height > 0:
                    self.jump_height -= self.fall_speed
                    if self.fall_speed < 10:
                        self.fall_speed += 0.5 * gravity
                else:
                    self.jump_height = 0
                    self.is_grounded = True
                    self.fall_speed = 0

            # Allow animation to continue while dead
            if bot.start_fire:
                self.frame_counter += 1
                if self.frame_counter >= self.frame_delay:
                    self.frame_counter = 0
                    if self.frame_index < len(self.current_animation) - 1:
                        self.frame_index += 1
                return
            
        current_time = pygame.time.get_ticks()
        if self.power_kick_hit and current_time >= 2000:
            self.power_kick_hit = False

         # Advance animation frame
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)

        # Normal jump logic
        if self.is_jumping:
            if self.jump_height < 200:
                self.jump_height += self.jump_speed
                if self.jump_speed > 0:
                    self.jump_speed -= 0.2
            else:
                self.is_jumping = False
                self.jump_speed = 10
        else:
            if self.jump_height > 0:
                self.jump_height -= self.fall_speed
                if self.fall_speed < 10:
                    self.fall_speed += 0.5 * gravity
            else:
                self.jump_height = 0
                self.is_grounded = True
                self.fall_speed = 0

        # Handle movement (left and right)
        if CONTROL_KEYS["left"] in keys_pressed:
            self.position_x -= self.move_speed
            self.is_flipped = True
        if CONTROL_KEYS["right"] in keys_pressed:
            self.position_x += self.move_speed
            self.is_flipped = False
         
        # Ensure the character stays within screen bounds
        # self.position_x = max(0, min(WIDTH - 150, self.position_x))
        self.position_x = max(-50, min(WIDTH - 150, self.position_x))
        self.position_y = max(0, min(HEIGHT - 200, self.position_y))

        # Update rect position for collisions
        offset_x = 50
        offset_y = 50
        self.rect.x = self.position_x + offset_x
        self.rect.y = self.position_y - self.jump_height + offset_y
    
    def draw(self, surface):
        # Get current frame
        img = self.current_animation[self.frame_index]
        
        # Calculate draw position
        draw_x = self.position_x 
        draw_y = self.position_y - self.jump_height

        # Flip if needed
        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)

        # Draw the character image
        surface.blit(img, (draw_x, draw_y))

    def set_animation(self, bot=None):
        if self.current_action == "dead" and not bot.start_fire:
            return
        
        if self.current_action == "idle":
            self.current_animation = self.idle_animation
            self.frame_delay = 5
            self.rect = pygame.Rect(
                self.position_x + 40,
                self.position_y - self.jump_height + 40,
                60, 100
            )
        elif self.current_action == "run":
            self.current_animation = self.run_animation
            self.frame_delay = 5
            self.rect = pygame.Rect(
                self.position_x + 40,
                self.position_y - self.jump_height + 40,
                60, 100
            )
        elif self.current_action == "kick":
            self.current_animation = self.kick_animation
            self.frame_delay = 5
            self.rect = pygame.Rect(
                self.position_x + 40,
                self.position_y - self.jump_height + 40,
                60, 100
            )
        elif self.current_action == "jump" and self.is_grounded:
            self.current_animation = self.jump_animation
            self.is_jumping = True
            self.is_grounded = False
            self.frame_delay = 5
            self.rect = pygame.Rect(
                self.position_x + 40,
                self.position_y - self.jump_height + 40,
                60, 100
            )
        elif self.current_action == "dead":
            self.current_animation = self.dead_animation
            self.is_dying = True
            self.frame_delay = 50
            self.rect = pygame.Rect(0,0,0,0)
            
             # Simulate falling down during death
            if self.jump_height > 0:
                self.jump_height -= self.fall_speed
                if self.fall_speed < 10:
                    self.fall_speed += 0.5 * gravity
            else:
                self.jump_height = 0
                self.is_grounded = True
                self.fall_speed = 0
            
        elif self.current_action == "hurt":
            self.current_animation = self.hurt_animation
            self.frame_delay = 5
            self.rect = pygame.Rect(
                self.position_x + 40,
                self.position_y - self.jump_height + 40,
                60, 100
            )
        self.frame_index = 0
        
    def draw(self, surface):
        img = self.current_animation[self.frame_index]
        draw_x = self.position_x 
        draw_y = self.position_y - self.jump_height

        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)

        # Draw the character image
        surface.blit(img, (draw_x, draw_y))

        # Draw the bounding rectangle (use same width/height as image)
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)

        
    def reset(self):
        """Reset character to starting position"""
        self.position_x = 100
        self.position_y = GROUND_Y
        self.is_jumping = False
        self.is_grounded = True
        self.jump_speed = 10
        self.fall_speed = 0
        self.jump_height = 0
        self.current_action = "idle"
        self.frame_index = 0
        self.current_animation = self.idle_animation  # FIXED: removed the "vvvvvvv" typo