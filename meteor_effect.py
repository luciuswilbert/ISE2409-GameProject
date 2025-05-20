import pygame

class MeteorEffect:
    def __init__(self, start_pos, end_pos, duration=50):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.counter = 0
        self.active = True
        self.trail = []

    def update(self):
        self.counter += 1
        if self.counter >= self.duration:
            self.active = False
        # Store the position for trail effect
        t = min(1, self.counter / self.duration)
        x = (1-t) * self.start_pos[0] + t * self.end_pos[0]
        y = (1-t) * self.start_pos[1] + t * self.end_pos[1]
        self.trail.append((x, y))
        # Limit the trail length
        if len(self.trail) > 20:
            self.trail.pop(0)

    def draw(self, screen):
        if not self.active:
            return
        # Draw trail first (older = more transparent)
        for i, pos in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            s = pygame.Surface((80,80), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,100,0,alpha), (40,40), 30)
            screen.blit(s, (pos[0]-40, pos[1]-40))
        # Draw "meteor" as big orange ball with glow
        t = min(1, self.counter / self.duration)
        x = (1-t) * self.start_pos[0] + t * self.end_pos[0]
        y = (1-t) * self.start_pos[1] + t * self.end_pos[1]
        # Glow
        s = pygame.Surface((100,100), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 200, 50, 120), (50,50), 50)
        screen.blit(s, (x-50, y-50))
        # Core
        pygame.draw.circle(screen, (255,60,0), (int(x), int(y)), 30)
        pygame.draw.circle(screen, (255,220,120), (int(x), int(y)), 16)
