
import pygame
from config import *
import random

class Bot:
    def __init__(self):
        def load_images(frame_list, resize=(110, 110)):
            loaded_images = []
            for frame in frame_list:
                try:
                    img = pygame.image.load(frame)
                    img = pygame.transform.scale(img, resize)
                    loaded_images.append(img)
                except pygame.error:
                    print(f"❌ Error: Could not load image {frame}")
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

    def update(self):
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

        offset_x = 0
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
        
    def draw(self, surface):
        img = self.current_animation[self.frame_index]
        draw_x = self.position_x 
        draw_y = self.position_y - self.jump_height + 50

        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)

        # Draw the character image
        surface.blit(img, (draw_x, draw_y))

        # Draw the bounding rectangle (use same width/height as image)
        # pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)
        
    def reset(self):
        self.__init__()
 
    def auto_chase(self, ball, player):
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




