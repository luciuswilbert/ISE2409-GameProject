import pygame
import os
import time
import math

class PowerBar:
    def __init__(self, is_player=True, level=1):
        self.is_player = is_player
        self.level = level  # Store the level
        self.last_update_time = time.time()
        self.cooldown_duration = 5  # 5 seconds total cooldown
        self.current_image_index = 5  # Start at powerbar_6 (empty)
        self.is_full = False
        self.paused = False
        
        # Load all 6 power bar images
        self.images = []
        for i in range(1, 7):  # powerbar_1.png to powerbar_6.png
            try:
                img_path = os.path.join("images", "power_bar", f"powerbar_{i}.png")
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (200, 60))
                self.images.append(img)
            except Exception as e:
                print(f"Error loading powerbar_{i}.png: {e}")
                # Create placeholder if image fails to load
                surf = pygame.Surface((200, 60), pygame.SRCALPHA)
                color = (255 - (i-1)*40, (i-1)*40, 0)  # Gradient from green to red
                surf.fill(color)
                self.images.append(surf)
        
        self.image = self.images[5]  # Start with empty (powerbar_6)
        
        # Font for power hints
        try:
            self.font = pygame.font.Font(None, 24)
            self.hint_font = pygame.font.Font(None, 28)
        except:
            print("Font loading failed")
            self.font = None
            self.hint_font = None
        
        # Pulsing effect for hint text
        self.pulse_timer = 0
        self.pulse_alpha = 255

    def use_power(self):
        """Attempt to use the power. Returns True if successful."""
        if self.is_full:
            self.current_image_index = 5  # Reset to empty (powerbar_6)
            self.image = self.images[5]
            self.is_full = False
            self.last_update_time = time.time()
            return True
        return False

    def update(self):
        """Update power bar state with countdown animation"""
        if not self.is_full and not self.paused:
            current_time = time.time()
            elapsed = current_time - self.last_update_time
            
            # Update image every second
            if elapsed >= 1.0:
                self.last_update_time = current_time
                
                # Move from powerbar_6 to powerbar_1
                if self.current_image_index > 0:
                    self.current_image_index -= 1
                    self.image = self.images[self.current_image_index]
                    
                    # When we reach powerbar_1, the bar is full
                    if self.current_image_index == 0:
                        self.is_full = True
        
        # Update pulsing effect for hint text when power is full
        if self.is_full:
            self.pulse_timer += 0.1
            self.pulse_alpha = int(abs(math.sin(self.pulse_timer)) * 127 + 128)

    def draw(self, screen):
        """Draw the power bar and hints"""
        if self.is_player:
            bar_pos = (20, 70)  # Player position (left side)
        else:
            bar_pos = (580, 70)  # Enemy position (right side)
        
        # Draw the power bar
        screen.blit(self.image, bar_pos)
        
        # Draw power hints when bar is full (only for player)
        if self.is_full and self.font and self.is_player:
            # Create hint text based on level
            if self.level == 1:
                hint_text = "Press 'P' for Sky Shot"  # Only Sky Shot in Level 1
            else:
                hint_text = "Press 'V' for Vine | Press 'P' for Sky Shot"  # Both powers available
            
            hint_surface = self.hint_font.render(hint_text, True, (255, 255, 255))
            hint_surface.set_alpha(self.pulse_alpha)
            
            # Position the hint below the power bar
            hint_x = bar_pos[0]
            hint_y = bar_pos[1] + 65
            
            # Draw semi-transparent background for better readability
            bg_rect = pygame.Rect(hint_x - 5, hint_y - 5, 
                                hint_surface.get_width() + 10, 
                                hint_surface.get_height() + 10)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 128))
            screen.blit(bg_surface, bg_rect.topleft)
            
            # Draw the hint text
            screen.blit(hint_surface, (hint_x, hint_y))

    def can_use_power(self):
        """Check if power can be used"""
        return self.is_full
    
    def pause(self):
        """Pause the power bar cooldown"""
        if not self.paused:
            self.paused = True
            self.pause_time = time.time()

    def resume(self):
        """Resume the power bar cooldown"""
        if self.paused:
            self.paused = False