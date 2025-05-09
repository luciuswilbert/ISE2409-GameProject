import pygame
from config import WIDTH, GROUND_Y, gravity
from collision import resolve_ball_obj_collision, resolve_ball_player_collision

class Ball:
    def __init__(self):
        self.radius = 15
        self.pos = [WIDTH // 2, 100]
        self.vel = [0, 0] # x for horizontal, y for vertical speed
        self.angle = 0  # Rotation angle in degrees
        self.bounciness = -0.8  # Fixed bounciness for testing
        
        # # TEST START ##
        # self.radius = 15
        # self.angle = 0  # Rotation angle in degrees
        # self.pos = [self.radius + 10, self.radius + 10]  # near top-left corner
        # self.rotation_speed = 0
        
        # angle_deg = 45  # launch angle
        # speed = 10       # initial push speed
        # angle_rad = math.radians(angle_deg)

        # self.vel = [
        #     speed * math.cos(angle_rad),   # x velocity → right
        #     -speed * math.sin(angle_rad)   # y velocity → up
        # ]
        # # TEST END ##
        
        # Load and scale the image
        self.original_image = pygame.image.load("images/ball/ball.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (self.radius * 2, self.radius * 2))
        self.image = self.original_image  # Will be rotated later

    def update(self, rects, player_objects, player, bot):
        self.vel[1] += gravity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        # Bounce off ground
        if self.pos[1] >= GROUND_Y - self.radius:
            self.pos[1] = GROUND_Y - self.radius
            self.vel[1] *= self.bounciness # vertical bounce
            self.vel[0] *= 0.99 # horizontal speed

        # Bounce off walls (edges of the screen)
        if self.pos[0] <= self.radius or self.pos[0] >= WIDTH - self.radius:
            self.vel[0] *= -1
            
        # for rect in rects:
        #     resolve_ball_obj_collision(self.pos, self.vel, self.radius, rect)
        for rect in rects:
            resolve_ball_obj_collision(self.pos, self.vel, self.radius, rect, bounce_factor=0.8)  # Adjust bounce factor for walls
            
        # Handle collisions with players
        for player in player_objects:  # player_objects is a list of Player instances
            player_rect = player.rect  # Access the player's rectangle
            resolve_ball_player_collision(self.pos, self.vel, self.radius, player_rect, bounce_factor=1)  # Correcting the call
        
        # Simulate rotational friction and update angle
        self.rotation_speed = self.vel[0] * 2
        self.rotation_speed *= 0.90  # decay factor (lower is more friction)
        self.angle += self.rotation_speed
        self.angle %= 360
        
        if abs(self.vel[0]) < 1e-4 and self.pos[1] == 365 and (self.pos[0] <= 30 or self.pos[0] >= 720):
            print("Ball stopped moving. Resetting position.")
            return True
        
        if self.pos[0] <= 0 or self.pos[0] >= WIDTH:
            print("Ball out of bounds. Resetting position.")
            return True
    
        return False
            

    def draw(self, screen):
        # Rotate the image and update position
        self.image = pygame.transform.rotate(self.original_image, -self.angle) # -self.angle for clockwise rotation
        rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        screen.blit(self.image, rect.topleft)
        
        # pygame.draw.rect(screen, (255, 0, 0), self.get_rect(), 2)

    def get_rect(self):
        return pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2, self.radius * 2)

    def reset(self):
        self.__init__()