# explosion_effect.py
import pygame

class ExplosionEffect:
    def __init__(self, frames, pos, duration=30):  # duration is in frames (e.g., 0.5s if 60 FPS)
        self.frames = frames
        self.pos = pos  # (x, y) center position
        self.total_frames = len(frames)
        self.duration = duration
        self.counter = 0
        self.frame_index = 0
        self.active = True

    def update(self):
        if not self.active:
            return
        self.counter += 1
        self.frame_index = int(self.counter / (self.duration / self.total_frames))
        if self.frame_index >= self.total_frames:
            self.active = False

    def draw(self, screen):
        if self.active and self.frame_index < self.total_frames:
            img = self.frames[self.frame_index]
            rect = img.get_rect(center=self.pos)
            screen.blit(img, rect)
