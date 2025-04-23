import pygame
from config import WIDTH, HEIGHT, GROUND_Y, gravity, bounciness
import math

GROUND_Y = HEIGHT - 30

class Ball:
    def __init__(self):
        # self.radius = 15
        # self.pos = [WIDTH // 2, 100]
        # self.vel = [0, 0] # x for horizontal, y for vertical speed
        # self.angle = 0  # Rotation angle in degrees
        
        ## TEST START ##
        self.radius = 15
        self.angle = 0  # Rotation angle in degrees
        self.pos = [self.radius + 10, self.radius + 10]  # near top-left corner
        self.rotation_speed = 0
        
        angle_deg = 45  # launch angle
        speed = 10       # initial push speed
        angle_rad = math.radians(angle_deg)

        self.vel = [
            speed * math.cos(angle_rad),   # x velocity → right
            -speed * math.sin(angle_rad)   # y velocity → up
        ]
        ## TEST END ##
        
        # Load and scale the image
        self.original_image = pygame.image.load("images/ball.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (self.radius * 2, self.radius * 2))
        self.image = self.original_image  # Will be rotated later

    # def update(self, goal_rects):
    def update(self):
        self.vel[1] += gravity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # Bounce off ground
        if self.pos[1] >= GROUND_Y - self.radius:
            self.pos[1] = GROUND_Y - self.radius
            self.vel[1] *= bounciness # vertical bounce
            self.vel[0] *= 0.99 # horizontal speed

        # Bounce off walls (edges of the screen)
        if self.pos[0] <= self.radius or self.pos[0] >= WIDTH - self.radius:
            self.vel[0] *= -1
            
        # for rect in goal_rects:
        #     resolve_circle_rect_collision(self.pos, self.vel, self.radius, rect)
        
        # Simulate rotational friction and update angle
        self.rotation_speed = self.vel[0] * 2
        self.rotation_speed *= 0.90  # decay factor (lower is more friction)
        self.angle += self.rotation_speed
        self.angle %= 360

    def draw(self, screen):
        # Rotate the image and update position
        self.image = pygame.transform.rotate(self.original_image, -self.angle) # -self.angle for clockwise rotation
        rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        screen.blit(self.image, rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2, self.radius * 2)

    def reset(self):
        self.__init__()