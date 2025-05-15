import pygame
import math
import random
from config import *
from sound_manager import play_sound

class PowerManager:
    def __init__(self, player, ball, arena, bot, power_bar):
        self.player = player
        self.ball = ball
        self.arena = arena
        self.bot = bot
        self.power_bar = power_bar  # Add reference to power bar
        self.level = arena.level  # ADDED: Store level from arena
        
        # Power Shot attributes - matching CharacterAnimation exactly
        self.is_power_active = False
        self.power_cooldown = 0
        self.power_cooldown_max = 180
        self.power_jump_height = 300
        self.power_jump_speed = 12
        self.power_ball = None
        self.has_fired_power_shot = False
        self.power_shot_height = 120
        self.power_frame_speed = 3
        self.power_animation_complete = False
        self.power_duration = 180
        self.power_timer = 0
        self.is_carrying_ball = False
        self.ball_offset_x = 50
        self.ball_offset_y = 50
        self.is_paused_at_peak = False
        self.hover_timer = 0
        self.hover_duration = 100  
        self.kick_animation_started = False
        self.is_in_animation_sequence = False
        self.complete_animation_regardless = False
        self.animation_locked = False
        
        # Load power animation
        self.power_frames = []
        for i in range(1, 11):
            img_path = f'images/player/Jump A-{str(i).zfill(2)}.png'
            try:
                img = pygame.image.load(img_path)
                img = pygame.transform.scale(img, (150, 200))
                self.power_frames.append(img)
            except pygame.error:
                pass
        
        # Load kick animation
        self.kick_frames = []
        kick_frames = ['images/player/Attack A-03.png', 'images/player/Attack A-04.png']
        for frame in kick_frames:
            try:
                img = pygame.image.load(frame)
                img = pygame.transform.scale(img, (150, 200))
                self.kick_frames.append(img)
            except pygame.error:
                pass
        
        # Vine power attributes - MODIFIED: Only load if level > 1
        self.vine_frames = []
        if self.level > 1:  # ADDED: Level check for vine frames
            for i in range(1, 6):
                # FIXED: Use relative path instead of absolute path
                img_path = f'images/Vine/vine{str(i)}.png'
                try:
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (80, 200))
                    self.vine_frames.append(img)
                except pygame.error:
                    pass
        
        # MODIFIED: Support for multiple vines
        self.is_vine_active = False
        self.vines = []  # List to store multiple vines
        self.max_vines = 3  # Maximum number of vines allowed at once
        self.vine_spacing = 100  # Horizontal spacing between vines
        self.vine_cooldown = 0
        self.vine_cooldown_max = 300
    
    def update(self, keys_pressed):
        # Update power bar
        self.power_bar.update()
        
        # Check for power activation (only if power bar is full)
        if pygame.K_p in keys_pressed and not self.is_power_active:
            self.activate_power()
        
        # Check for vine activation (only if power bar is full AND level > 1)
        if pygame.K_v in keys_pressed and not self.is_vine_active:
            if self.level > 1:  # ADDED: Level check
                self.activate_vine()
        
        # Update power shot
        if self.is_power_active:
            self.update_power_shot()
        
        # Update all vines
        self.update_vines()
    
    def activate_power(self):
        """Activate power shot - checks power bar"""
        if self.power_bar.can_use_power() and self.player.is_grounded and not self.is_power_active:
            # Use the power from the power bar
            if self.power_bar.use_power():
                self.is_power_active = True
                self.power_ball = self.ball
                self.is_carrying_ball = True
                self.player.is_flipped = False
                
                # FIXED: Immediately teleport to hover position like CharacterAnimation
                self.player.jump_height = self.power_jump_height  # Instant jump to peak
                self.is_paused_at_peak = True  # Start in hover state
                self.power_jump_speed = 0  # No vertical movement initially
                self.player.is_grounded = False
                self.has_fired_power_shot = False
                self.hover_timer = 0
                self.kick_animation_started = False
                self.power_timer = 0
                self.is_in_animation_sequence = False
                self.complete_animation_regardless = False
                self.animation_locked = False
                
                # FIXED: Start with idle animation while hovering (not power animation)
                self.player.current_action = "idle"
                self.player.current_animation = self.player.idle_animation
                self.player.frame_index = 0
                
                # Get the ball and position it with the character
                self._update_carried_ball_position()
                
                # Pause bot and timer
                self.bot.pause()
                self.arena.pause_timer()
                return True
        return False
    
    def activate_vine(self):
        """Activate vine power - checks power bar and creates more concentrated vines"""
        if self.level == 1:  # Level check
            return False
            
        if self.power_bar.can_use_power() and len(self.vines) < self.max_vines and self.vine_frames:
            # Use the power from the power bar
            if self.power_bar.use_power():
                play_sound('vine_power')
                self.is_vine_active = True
                
                # Create base position for the new vine group
                base_x = 50 + (len(self.vines) * self.vine_spacing)
                
                # Create the main vine - INCREASED width from 80 to 100
                main_vine = {
                    'animation_timer': 0,
                    'frame_index': 0,
                    'position': [base_x, GROUND_Y],
                    'rect': pygame.Rect(base_x - 50, GROUND_Y - 200, 100, 200),  # Wider rect
                    'animation_duration': 60,
                    'hold_duration': 180,
                    'active': True
                }
                
                # INCREASED: Create more side vines (5 instead of 2) with smaller spacing
                side_vines = []
                
                # Create 5 side vines with smaller spacing between them
                side_positions = [-60, -30, 0, 30, 60]  # Closer together
                
                for offset in side_positions:
                    side_vine = {
                        'animation_timer': 0,
                        'frame_index': 0,
                        'position': [base_x + offset, GROUND_Y],
                        'rect': pygame.Rect(base_x + offset - 25, GROUND_Y - 180, 50, 180),
                        'animation_duration': 70 + random.randint(-10, 10),  # Varied growth speed
                        'hold_duration': 180,
                        'active': True,
                        'scale': 0.7 + random.uniform(-0.1, 0.1)  # Varied scales
                    }
                    side_vines.append(side_vine)
                
                # Add all vines to the list
                vine_group = {
                    'main': main_vine,
                    'sides': side_vines
                }
                
                self.vines.append(vine_group)
                return True
        return False

    def update_power_shot(self):
        """Update power shot animation and physics - FIXED"""
        # Power timer to force end if needed
        self.power_timer += 1
        if self.power_timer > self.power_duration:
            self._end_power_mode()
            return
        
        # Update animation frame
        self.player.frame_counter += 1
        if self.player.frame_counter >= (self.player.frame_delay if self.player.current_action != "power" else self.power_frame_speed):
            self.player.frame_counter = 0
            
            # Special handling for kick animation during hover
            if self.kick_animation_started:
                # Only advance to the next frame if we're not at the last kick frame
                if self.player.frame_index < len(self.kick_frames) - 1:
                    self.player.frame_index += 1
                    
                    # IMPORTANT: Fire the shot exactly when the kick animation starts displaying
                    if self.player.frame_index == 1 and not self.has_fired_power_shot:
                        self._fire_power_shot()
                        self.has_fired_power_shot = True
                        self.is_carrying_ball = False
                        
                        # Set flags to complete animation
                        self.complete_animation_regardless = True
                        self.animation_locked = True
            else:
                # For other animations, cycle through frames normally
                self.player.frame_index = (self.player.frame_index + 1) % len(self.player.current_animation)
        
        # FIXED: We're already at peak height (teleported there), so handle hover logic
        if self.is_paused_at_peak and not self.has_fired_power_shot:
            self.hover_timer += 1
            
            # Update ball position during hover
            if self.is_carrying_ball and self.power_ball:
                self._update_carried_ball_position()
            
            # Start kick animation when hover timer reaches threshold
            if self.hover_timer >= 50 and not self.kick_animation_started:  # FIXED: Match CharacterAnimation (50 frames)
                # Switch to kick animation
                self.player.current_animation = self.kick_frames
                self.player.frame_index = 0
                self.kick_animation_started = True
                play_sound('power_shot')
        
        # Falling down after shot
        if self.has_fired_power_shot:
            # Start falling
            self.power_jump_speed -= 0.5  # FIXED: Match CharacterAnimation's fall speed
            self.player.jump_height += self.power_jump_speed
            
            if self.player.jump_height <= 0:
                self._end_power_mode()  # End power mode once landed
    
    def update_vines(self):
        """Update all vine animations"""
        # Create a list to track which vine groups to remove
        vines_to_remove = []
        
        # Update each vine group
        for i, vine_group in enumerate(self.vines):
            # Update main vine
            vine_group['main']['animation_timer'] += 1
            
            # First second - animate through frames
            if vine_group['main']['animation_timer'] < vine_group['main']['animation_duration']:
                if vine_group['main']['animation_timer'] % 12 == 0:
                    vine_group['main']['frame_index'] = min(
                        vine_group['main']['frame_index'] + 1, 
                        len(self.vine_frames) - 1
                    )
            
            # After animation + hold time, deactivate
            elif vine_group['main']['animation_timer'] >= (
                    vine_group['main']['animation_duration'] + 
                    vine_group['main']['hold_duration']
                ):
                vines_to_remove.append(i)
                continue
            
            # Update side vines
            for side_vine in vine_group['sides']:
                side_vine['animation_timer'] += 1
                
                # First second - animate through frames
                if side_vine['animation_timer'] < side_vine['animation_duration']:
                    if side_vine['animation_timer'] % 14 == 0:  # Slightly slower than main vine
                        side_vine['frame_index'] = min(
                            side_vine['frame_index'] + 1, 
                            len(self.vine_frames) - 1
                        )
        
        # Remove completed vine groups (in reverse order to avoid index issues)
        for i in sorted(vines_to_remove, reverse=True):
            del self.vines[i]
        
        # Update is_vine_active flag based on if any vines exist
        self.is_vine_active = len(self.vines) > 0
    
    def draw_power_effects(self, surface):
        """Draw power effects"""
        # Draw all vine animations if active
        if self.vine_frames:
            for vine_group in self.vines:
                # Draw main vine
                main_vine = vine_group['main']
                if main_vine['active'] and main_vine['frame_index'] < len(self.vine_frames):
                    self._draw_single_vine(surface, main_vine, 1.0)  # Full size
                
                # Draw side vines
                for side_vine in vine_group['sides']:
                    if side_vine['active'] and side_vine['frame_index'] < len(self.vine_frames):
                        self._draw_single_vine(surface, side_vine, side_vine.get('scale', 0.75))  # Smaller scale
    
    def _draw_single_vine(self, surface, vine_data, scale=1.0):
        """Helper method to draw a single vine with given parameters"""
        vine_frame = self.vine_frames[vine_data['frame_index']]
        
        # Calculate growth factor
        if vine_data['animation_timer'] < vine_data['animation_duration']:
            growth_factor = vine_data['animation_timer'] / vine_data['animation_duration']
        else:
            growth_factor = 1.0
        
        # MODIFIED: Scale width more to make vines appear denser
        original_width = vine_frame.get_width() * scale * 1.4  # 40% wider
        original_height = vine_frame.get_height() * scale
        new_height = int(original_height * growth_factor)
        
        if new_height > 0:
            scaled_vine = pygame.transform.scale(vine_frame, (int(original_width), new_height))
            vine_draw_pos = [
                vine_data['position'][0] - scaled_vine.get_width()//2,
                vine_data['position'][1] - new_height
            ]
            surface.blit(scaled_vine, vine_draw_pos)
            
            # Update collision rect
            if 'rect' in vine_data:
                vine_data['rect'].height = new_height
                vine_data['rect'].y = vine_data['position'][1] - new_height
    
    def get_vine_rect(self):
        """Return all vine collision rects as a list"""
        vine_rects = []
        for vine_group in self.vines:
            # Add main vine rect
            if vine_group['main']['rect']:
                vine_rects.append(vine_group['main']['rect'])
            
            # Add side vine rects
            for side_vine in vine_group['sides']:
                if side_vine['rect']:
                    vine_rects.append(side_vine['rect'])
            
        return vine_rects if vine_rects else None
    
    def _update_carried_ball_position(self):
        """Update ball position when character is carrying it during power jump"""
        if self.power_ball and hasattr(self.power_ball, 'pos'):
            # Force character to face right during power move
            self.player.is_flipped = False
            
            # Position ball more to the right of the character
            offset_x = 100  # Further to the right
            offset_y = 135  # Upper body level
            
            # Position the ball relative to character
            self.power_ball.pos[0] = self.player.position_x + offset_x
            self.power_ball.pos[1] = self.player.position_y - self.player.jump_height + offset_y
            
            # Zero out the ball's velocity while it's being carried
            self.power_ball.vel = [0, 0]
    
    def _fire_power_shot(self):
        """Fire the power shot from the character's position"""
        if self.power_ball and hasattr(self.power_ball, 'pos'):
            # Force character to face right
            self.player.is_flipped = False
            
            # Position the ball near the character's leg for the kick
            leg_offset_x = min(110, WIDTH - self.player.position_x - 50)  # Limit offset when close to edge
            leg_offset_y = 140  # At leg height
            
            # Set ball position precisely relative to character
            self.power_ball.pos[0] = self.player.position_x + leg_offset_x
            self.power_ball.pos[1] = self.player.position_y - self.player.jump_height + leg_offset_y
            
            # Dynamically choose target based on position
            if self.player.position_x > WIDTH * 0.7:  # If close to right side
                target_x = 50  # Target left goal
                target_y = 470
            else:
                target_x = 750  # Target right goal
                target_y = 470
            
            # Calculate direction vector
            dx = target_x - self.power_ball.pos[0]
            dy = target_y - self.power_ball.pos[1]
            
            # Normalize and scale for powerful shot
            magnitude = (dx**2 + dy**2)**0.5
            if magnitude > 0:
                dx = dx / magnitude * 15
                dy = dy / magnitude * 8
            
            # Apply the power shot
            self.power_ball.vel[0] = dx
            self.power_ball.vel[1] = dy
            
            # Activate special effect
            if hasattr(self.power_ball, 'activate_special_effect'):
                self.power_ball.activate_special_effect(self)
            else:
                self.power_ball.activate_special_effect()
    
    def _end_power_mode(self):
        """Helper to safely end power mode and return to idle"""
        self.player.jump_height = 0
        self.is_power_active = False
        self.has_fired_power_shot = False
        self.player.is_grounded = True
        self.power_jump_speed = 12  # Reset for next time
        self.power_animation_complete = False
        self.power_timer = 0  # Reset timer
        self.is_carrying_ball = False
        self.hover_timer = 0  # Reset hover timer
        self.kick_animation_started = False
        self.player.current_action = "idle"
        self.is_in_animation_sequence = False
        self.complete_animation_regardless = False
        self.animation_locked = False
        self.player.set_animation()
        
        # Resume bot and timer
        if self.bot.is_paused:
            # Give the bot a proper reset before resuming
            self.bot.is_jumping = False
            self.bot.jump_height = 0
            self.bot.is_grounded = True
            self.bot.current_action = "idle"
            self.bot.current_animation = self.bot.idle_animation
            self.bot.frame_index = 0
            
            # Now properly resume the bot
            self.bot.resume()
            self.arena.resume_timer()
    
    def reset(self):
        """Safely reset character state"""
        if self.is_power_active:
            self._end_power_mode()
        
        # Reset animation flags regardless of current state
        self.animation_locked = False
        self.is_in_animation_sequence = False
        self.complete_animation_regardless = False
        
        # Reset all vines
        self.is_vine_active = False
        self.vines = []  # Clear all vine groups
        
        # Always make sure bot is unpaused after any reset
        if self.bot.is_paused:
            self.bot.resume()
        
        return True
