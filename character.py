import pygame
from config import *

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
                    print(f"❌ Error: Could not load image {frame}")
            return loaded_images

        idle_frames = [f'images/player/Idle A-{str(i).zfill(2)}.png' for i in range(1, 7)]
        run_frames = [f'images/player/Run A-{str(i).zfill(2)}.png' for i in range(1, 9)]
        kick_frames = ['images/player/Attack A-03.png', 'images/player/Attack A-04.png']
        jump_frames = [f'images/player/Jump A-{str(i).zfill(2)}.png' for i in range(1, 11)]

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
        self.is_flipped = False
        self.position_x = 100
        self.position_y = GROUND_Y
        self.move_speed = 5
        self.rect = pygame.Rect(
            self.position_x + 40,
            self.position_y - self.jump_height + 40,
            50, 80
        )
    def update(self, keys_pressed):
        # Update animation frame
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
        self.position_x = max(0, min(WIDTH - 150, self.position_x))
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