import pygame
import random
from config import *

class SmokeParticle:
    def __init__(self, x, y, color, type="flame"):
        self.x = x
        self.y = y
        self.radius = random.randint(5, 10)
        self.color = color
        self.type = type
        self.life = 250
        self.vel_x = random.uniform(-1, 1)
        self.vel_y = random.uniform(-3, -1)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life -= 2

        if self.type == "flame":
            # Define three vertical levels
            transition_start = HEIGHT
            transition_mid = random.uniform(HEIGHT * 0.9, HEIGHT * 0.8)  # Flame to grey
            transition_top = random.uniform(HEIGHT * 0.4, HEIGHT * 0.2)  # Flame to white
            transition_fade = random.uniform(HEIGHT * 0.05, HEIGHT * 0.01)  # Fade

            if self.y > transition_mid:
                # Bottom: orange to grey
                relative_height = (transition_start - self.y) / (transition_start - transition_mid)
                r = int(255 - (255 - 50) * relative_height)
                g = int(100 - (100 - 50) * relative_height)
                b = int(0 + (50 - 0) * relative_height)
                alpha = 200
            elif self.y > transition_top:
                # Middle: grey to white
                relative_height = (transition_mid - self.y) / (transition_mid - transition_top)
                r = int(50 + (255 - 50) * relative_height)
                g = int(50 + (255 - 50) * relative_height)
                b = int(50 + (255 - 50) * relative_height)
                alpha = int(200 * (1 - relative_height))  # fade out
            elif self.y > transition_fade:
                # Top: grey to white
                relative_height = (transition_top - self.y) / (transition_top - transition_fade)
                r = int(255 * relative_height)
                g = int(255 * relative_height)
                b = int(255 * relative_height)
                alpha = int(200 * (1 - relative_height))
            else:
                # Top: full white
                r, g, b = 255, 255, 255
                alpha = 0

        self.color = (r, g, b, alpha)




    def draw(self, surface):
        # if self.life > 0:
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            # Use self.color (which already includes alpha) directly
            pygame.draw.circle(s, self.color, (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))
