import math
import pygame
from config import WIDTH, GROUND_Y, gravity, DEBUG_MODE
from collision import resolve_ball_obj_collision, resolve_ball_player_collision, bot_power_kick_player_ball_collision
from character import CharacterAnimation
import random
from sound_manager import play_sound
from botLevel1 import BotLevel1

class Ball:
    def __init__(self, current_level=1):
        self.radius = 15
        self.pos = [WIDTH // 2, 100]
        self.vel = [0, 0] # x for horizontal, y for vertical speed
        self.angle = 0  # Rotation angle in degrees
        self.bounciness = -0.8  # Fixed bounciness for testing
        self.prev_y = self.pos[1]
        self.ground_collision_threshold = 2.0
        if current_level == 1:
            self.HORIZONTAL_FORCE_SCALE = 0.6
        else:
            self.HORIZONTAL_FORCE_SCALE = 0.7
        self.VERTICAL_FORCE_SCALE = 1
        self.meteor_locked = False  # Add to track if the meteor is carrying the ball
        
        # Track who kicked the ball last
        self.last_kicked_by_player = True  # True for player/character, False for demon/bot
        self.arena = None  # Reference to arena (will be set in GameLevel1)
        
        # Load and scale the normal image
        self.original_image = pygame.image.load("images/ball/ball.png").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (self.radius * 2, self.radius * 2))
        self.image = self.original_image  # Will be rotated later
        
        # Special effect properties
        self.special_effect_active = False
        self.special_effect_duration = 800  # Increased duration for longer effect
        self.special_effect_timer = 0
        self.character_ref = None  # Reference to character animation
        
        # Load power frames for special effect
        self.power_frames = []
        for i in range(1, 41):
            try:
                frame = pygame.image.load(f"images/power_frame/{str(i).zfill(2)}.png").convert_alpha()
                # INCREASED SIZE from 240x240 to 300x300 for more obvious effect
                frame = pygame.transform.scale(frame, (300, 300))
                self.power_frames.append(frame)
            except pygame.error:
                print(f"❌ Error: Could not load power frame {i}")
        
        self.power_frame_index = 0
        self.power_frame_delay = 2  # FASTER animation speed (reduced from 3 to 2)
        self.power_frame_counter = 0
        
        # Store previous positions for the trail effect
        self.previous_positions = []
        self.max_trail_length = 10  # INCREASED from 8 to 10 for longer trail
        # INCREASED opacity values for more visible trail
        self.frame_opacity = [255, 240, 225, 210, 195, 180, 160, 140, 120, 100]  # Higher opacity values
        
        # Add particle effect properties
        self.particles = []
        self.max_particles = 30  # INCREASED from 20 to 30
        
        # Track the current direction of the ball
        self.direction = 0  # Angle in degrees (0 = right, 90 = down, 180 = left, 270 = up)
        
        # Visual effect pulse (new)
        self.pulse_timer = 0
        self.pulse_scale = 1.0

        # Load and keep copies of original frames for scaling effects
        self.original_power_frames = []
        if self.power_frames:
            for frame in self.power_frames:
                self.original_power_frames.append(frame.copy())
        
        # Add tracking for recent kicks to better handle kick detection
        self.last_touch_timer = 0  # Changed from last_kick_timer
        self.touch_cooldown = 10  # Changed from kick_cooldown - frames between touches
        
        # For collision visualization
        self.collision_flash = 0
    
    def set_last_touched(self, by_player):  # Changed method name
        """Set who touched the ball last and update arena"""
        self.last_kicked_by_player = by_player
        if self.arena:
            self.arena.ball_last_kicked_by_character = by_player
            print(f"Ball touched by: {'CHARACTER' if by_player else 'DEMON'}")
        
        # Reset touch timer
        self.last_touch_timer = self.touch_cooldown
    
    def check_player_collision(self, player, bot):
        """Track any collision with the ball as a valid touch, kicks apply more force"""
        ball_rect = self.get_rect()
        collision_occurred = False
        
        # Reduce touch timer each frame - SHORTENED TIMER
        if self.last_touch_timer > 0:
            self.last_touch_timer -= 2  # Reduce faster to allow quicker re-collisions
        
        # Check if ball is on the ground or close to it
        is_ball_on_ground = abs(self.pos[1] - (GROUND_Y - self.radius)) < 10 and abs(self.vel[1]) < 2.0
        is_stationary = abs(self.vel[0]) < 0.5 and abs(self.vel[1]) < 0.5 and is_ball_on_ground
        
        # Check collision with player/character
        if ball_rect.colliderect(player.rect) and self.last_touch_timer <= 0:
            collision_occurred = True
            
            # Check if player is kicking
            is_kicking = False
            if hasattr(player, 'current_action'):
                is_kicking = player.current_action == "kick"
                # Also check if player just finished kicking
                if hasattr(player, 'frame_counter') and player.current_action != "kick":
                    # Check if we just transitioned from kick
                    if hasattr(player, 'last_action') and player.last_action == "kick":
                        is_kicking = True
            
            # Apply force based on player's direction and position
            player_center = player.rect.center
            ball_center = self.pos
            
            # Calculate direction from player to ball
            dx = ball_center[0] - player_center[0]
            dy = ball_center[1] - player_center[1]
            distance = max((dx**2 + dy**2)**0.5, 0.1)  # Avoid division by zero
            
            if is_stationary:
                # For stationary balls, apply stronger directional force based on player facing
                player_facing_right = not player.is_flipped
                kick_direction = 1 if player_facing_right else -1
                
                if is_kicking:
                    # Set velocity directly rather than adding
                    self.vel[0] = kick_direction * 8 * self.HORIZONTAL_FORCE_SCALE
                    self.vel[1] = -4 * self.VERTICAL_FORCE_SCALE # Add upward component
                else:
                    self.vel[0] = kick_direction * 4 * self.HORIZONTAL_FORCE_SCALE
                    self.vel[1] = -2 * self.VERTICAL_FORCE_SCALE
                
                print("MOVING STATIONARY BALL: Direction", "right" if kick_direction > 0 else "left")
                play_sound('ball_kick')
            else:
                if is_kicking:
                    # Stronger force for kicks
                    force_magnitude = 10  # Increased kick strength
                    self.vel[0] += (dx / distance) * force_magnitude * self.HORIZONTAL_FORCE_SCALE
                    self.vel[1] += (dy / distance) * force_magnitude * self.VERTICAL_FORCE_SCALE
                    print("NORMAL KICK: Ball kicked by CHARACTER")
                    play_sound('ball_kick')
                else:
                    # Weaker force for just touching
                    force_magnitude = 5  # Gentle touch force
                    self.vel[0] += (dx / distance) * force_magnitude * self.HORIZONTAL_FORCE_SCALE
                    self.vel[1] += (dy / distance) * force_magnitude * 0.5 * self.VERTICAL_FORCE_SCALE
                    print("TOUCH: Ball touched by CHARACTER")
                    play_sound('ball_kick')
            
            # Track that player touched/kicked the ball (REGARDLESS of kick action)
            self.set_last_touched(True)
        
        # Check collision with bot/demon - Apply similar changes to bot collision
        if ball_rect.colliderect(bot.rect) and self.last_touch_timer <= 0:
            collision_occurred = True
            
            # IMPROVED: Check if bot is kicking more reliably
            is_kicking = False
            if hasattr(bot, 'current_action'):
                is_kicking = bot.current_action == "kick"
                # Also check recent kick transition for bot
                if hasattr(bot, 'last_action') and bot.last_action == "kick":
                    is_kicking = True
            
            # IMPROVED: Always ensure minimum force on collision
            bot_center = bot.rect.center
            ball_center = self.pos
            
            # Calculate direction from bot to ball
            dx = ball_center[0] - bot_center[0]
            dy = ball_center[1] - bot_center[1]
            distance = max((dx**2 + dy**2)**0.5, 1)  # Prevent division by zero
            
            # Normalize direction
            norm_dx = dx / distance
            norm_dy = dy / distance
            
            if is_stationary:
                # Apply stronger force to stationary balls
                bot_facing_right = not bot.is_flipped
                kick_direction = 1 if bot_facing_right else -1
                
                if is_kicking:
                    self.vel[0] = kick_direction * 12 * self.HORIZONTAL_FORCE_SCALE
                    self.vel[1] = -6 * self.VERTICAL_FORCE_SCALE # Higher upward component for demon
                else:
                    self.vel[0] = kick_direction * 6 * self.HORIZONTAL_FORCE_SCALE
                    self.vel[1] = -3 * self.VERTICAL_FORCE_SCALE
                    
                print("BOT MOVING STATIONARY BALL: Direction", "right" if kick_direction > 0 else "left")
                play_sound('ball_kick')
            else:
                if is_kicking:
                    # Stronger force for kicks
                    force_magnitude = 15  # Increased kick strength
                    
                    # If ball is on ground, add more upward force
                    if is_ball_on_ground:
                        # Apply horizontal force based on bot direction
                        kick_direction = -1 if bot.is_flipped else 1
                        self.vel[0] = kick_direction * force_magnitude * 0.7 * self.HORIZONTAL_FORCE_SCALE
                        
                        # Strong upward force - sky-high kick
                        self.vel[1] = -force_magnitude * 1.2 * self.VERTICAL_FORCE_SCALE
                        print("SKY KICK: Ball kicked high into the air by DEMON")
                    else:
                        self.vel[0] += norm_dx * force_magnitude * self.HORIZONTAL_FORCE_SCALE
                        self.vel[1] += norm_dy * force_magnitude * self.VERTICAL_FORCE_SCALE
                        print("NORMAL KICK: Ball kicked by DEMON")
                    
                    play_sound('ball_kick')
                else:
                    # IMPROVED: Guarantee minimum response force even for touches
                    force_magnitude = 6  # Slightly increased minimum force
                    
                    # Current velocity magnitude
                    current_vel_mag = (self.vel[0]**2 * self.HORIZONTAL_FORCE_SCALE + self.vel[1]**2 * self.VERTICAL_FORCE_SCALE)**0.5
                    
                    # If ball is on ground, add some upward force even for touch
                    if is_ball_on_ground:
                        self.vel[0] += norm_dx * force_magnitude
                        self.vel[1] = -force_magnitude * 0.7  * self.VERTICAL_FORCE_SCALE # Increased upward bounce for touch
                        print("GROUND TOUCH: Ball nudged upward by DEMON")
                    else:
                        # IMPROVED: If current velocity is low, apply a minimum force
                        if current_vel_mag < 2.0:
                            self.vel[0] = norm_dx * force_magnitude *  self.HORIZONTAL_FORCE_SCALE
                            self.vel[1] = norm_dy * force_magnitude * 0.7 * self.VERTICAL_FORCE_SCALE
                        else:
                            # Otherwise add to current velocity
                            self.vel[0] += norm_dx * force_magnitude * self.HORIZONTAL_FORCE_SCALE
                            self.vel[1] += norm_dy * force_magnitude * 0.6 * self.VERTICAL_FORCE_SCALE
                        
                        print("TOUCH: Ball touched by DEMON")
                    
                    play_sound('ball_kick')
            
            # Track that demon touched/kicked the ball
            self.set_last_touched(False)
            
            # IMPROVED: Set a shorter touch timer to prevent immediate re-collision
            self.last_touch_timer = 8  # Shortened from likely 10-15 frames
        
        # Add visual collision effect if in debug mode
        if collision_occurred and DEBUG_MODE:
            self.collision_flash = 10
        
        return collision_occurred

    # UPDATED: Now handles a list of vine rectangles instead of a single rectangle
    def check_vine_collision(self, vine_rects):
        """Check collision with vines and handle rebound - always bounce to the right"""
        if not vine_rects:  # Handle None or empty list case
            return False
            
        # Get the ball's collision rect
        ball_rect = self.get_rect()
        
        # Check for collision with any vine rect in the list
        for vine_rect in vine_rects:
            if ball_rect.colliderect(vine_rect):
                print(f"Vine collision detected! Ball pos: {self.pos}, Vine rect: {vine_rect}")  # Debug print
                
                # Play ball touch sound for vine collision
                play_sound('ball_kick')
                
                # Always make the ball bounce to the right
                self.vel[0] = abs(self.vel[0]) * 1.5  # Force positive X velocity (right direction)
                if self.vel[0] < 5:  # Ensure minimum speed
                    self.vel[0] = 5
                
                # Position the ball to the right of the vine to prevent multiple collisions
                self.pos[0] = vine_rect.right + self.radius + 5
                
                # Add upward bounce effect
                if self.vel[1] > 0:  # Ball moving down
                    self.vel[1] = -abs(self.vel[1]) * 0.8
                else:  # Ball moving up or stationary
                    self.vel[1] = -5  # Give it an upward bounce
                
                # Add some randomness to make it more realistic
                self.vel[0] += random.uniform(0, 3)  # Only add positive randomness to keep it going right
                self.vel[1] += random.uniform(-2, 2)
                
                # If special effect is active, maintain its properties
                if self.special_effect_active:
                    # Keep the special effect but adjust direction
                    self.vel[0] = abs(self.vel[0]) * 1.2

                self.set_last_touched(True)
                
                # Add collision flash for visualization in debug mode
                if DEBUG_MODE:
                    self.collision_flash = 10
                    
                print(f"Ball rebounded to the right! New velocity: {self.vel}")  # Debug print
                return True
        return False

    def update(self, rects, player_objects, player, bot):
        # ======= BEGIN: Meteor Carrying Ball Logic ========
        if self.arena and getattr(self.arena, "meteor_ball_locked", False):
            # Force the ball position to the meteor position
            self.pos[0] = self.arena.meteor_ball_x
            self.pos[1] = self.arena.meteor_ball_y
            self.vel = [0, 0]  # Lock velocity as well
            # (Skip ALL OTHER PHYSICS and COLLISION!)
            return False  # Do not update ball, do not allow goal until meteor lands
        # ======= END: Meteor Carrying Ball Logic ========

        # Handle collision flash countdown
        if hasattr(self, 'collision_flash') and self.collision_flash > 0:
            self.collision_flash -= 1
            
        # Store previous position for ground collision detection
        self.prev_y = self.pos[1]
        
        # Check player collisions to track who kicked the ball (DO THIS FIRST)
        self.check_player_collision(player, bot)
        
        # Check if we should keep special effect active due to character animation
        if self.special_effect_active and self.character_ref and hasattr(self.character_ref, 'animation_locked'):
            if self.character_ref.animation_locked:
                # Keep the special effect alive if the character is in locked animation
                self.special_effect_timer = max(120, self.special_effect_timer)
        
        # Update the ball's direction based on velocity
        vel_magnitude = (self.vel[0]**2 * self.HORIZONTAL_FORCE_SCALE + self.vel[1]**2 * self.VERTICAL_FORCE_SCALE)**0.5
        if vel_magnitude > 0.5:  # Only update direction if ball is moving
            # Calculate angle in degrees (0-360)
            self.direction = math.degrees(math.atan2(self.vel[1] * self.VERTICAL_FORCE_SCALE, self.vel[0] * self.HORIZONTAL_FORCE_SCALE)) % 360
        
        # Store previous position for trail effect
        if self.special_effect_active:
            # Calculate trail position BEHIND the ball (opposite of velocity direction)
            if vel_magnitude > 0:
                # Calculate position 180 degrees opposite to the direction of travel
                trail_angle = (self.direction + 180) % 360
                trail_angle_rad = math.radians(trail_angle)
                trail_distance = 80  # Distance behind ball
                
                trail_pos_x = self.pos[0] + math.cos(trail_angle_rad) * trail_distance
                trail_pos_y = self.pos[1] + math.sin(trail_angle_rad) * trail_distance
            else:
                trail_pos_x, trail_pos_y = self.pos[0], self.pos[1]
                
            # Only store position if we've moved a significant distance
            if len(self.previous_positions) == 0 or \
               ((trail_pos_x - self.previous_positions[-1][0])**2 + 
                (trail_pos_y - self.previous_positions[-1][1])**2) > 70:
                
                self.previous_positions.append([trail_pos_x, trail_pos_y, self.power_frame_index, self.direction])
                
                # Limit the trail length
                if len(self.previous_positions) > self.max_trail_length:
                    self.previous_positions.pop(0)
                    
                # Add particles around the ball when special effect is active
                if random.random() < 0.25:  # 25% chance each frame
                    for _ in range(3):
                        # Create particles slightly behind the ball based on velocity
                        particle_angle = (self.direction + 180) % 360 + random.uniform(-30, 30)
                        particle_angle_rad = math.radians(particle_angle)
                        particle_distance = random.uniform(5, 20)
                        
                        offset_x = math.cos(particle_angle_rad) * particle_distance
                        offset_y = math.sin(particle_angle_rad) * particle_distance
                            
                        particle = {
                            'pos': [self.pos[0] + offset_x, self.pos[1] + offset_y],
                            'vel': [random.uniform(-2.0, 2.0), random.uniform(-2.0, 2.0)],
                            'radius': random.uniform(2, 6),
                            'lifetime': 30,
                            'color': (random.randint(200, 255), 
                                     random.randint(100, 255), 
                                     random.randint(50, 150))
                        }
                        self.particles.append(particle)
            
            # Update particles
            for particle in self.particles[:]:
                particle['pos'][0] += particle['vel'][0]
                particle['pos'][1] += particle['vel'][1]
                particle['lifetime'] -= 1
                if particle['lifetime'] <= 0:
                    self.particles.remove(particle)
            
            # Update power frame animation
            self.power_frame_counter += 1
            if self.power_frame_counter >= self.power_frame_delay:
                self.power_frame_counter = 0
                self.power_frame_index = (self.power_frame_index + 1) % len(self.power_frames)
            
            # Update special effect timer
            self.special_effect_timer -= 1
            if self.special_effect_timer <= 0:
                self.special_effect_active = False
                self.previous_positions = []  # Clear trail when effect ends
                self.particles = []  # Clear particles
                self.bounciness = -0.8  # Reset bounciness to normal
                self.character_ref = None  # Clear character reference
        else:
            # Clear trail if effect is not active
            self.previous_positions = []
            self.particles = []
        
        # Normal physics updates
        if self.special_effect_active:
            # Almost no gravity for special effect to maintain a flat trajectory
            self.vel[1] += gravity * 0.1 * self.VERTICAL_FORCE_SCALE # Just 10% of normal gravity
            
            # Add a slight downward force to keep the shot low to the ground
            # This helps ensure the ball stays close to the ground
            if self.pos[1] < GROUND_Y - self.radius - 50:  # If ball is more than 50px above ground
                self.vel[1] += 0.15 * self.VERTICAL_FORCE_SCALE # Gentle downward push to keep shot low
        else:
            # Normal gravity
            self.vel[1] += gravity * self.VERTICAL_FORCE_SCALE
        
        # If special effect is active, adjust the ball's movement speed
        if self.special_effect_active:
            speed_factor = 1.2  # Ball moves at 120% normal speed
            self.pos[0] += self.vel[0] * speed_factor *  self.HORIZONTAL_FORCE_SCALE
            self.pos[1] += self.vel[1] * speed_factor * self.VERTICAL_FORCE_SCALE
        else:
            # Normal movement
            self.pos[0] += self.vel[0] * self.HORIZONTAL_FORCE_SCALE
            self.pos[1] += self.vel[1] * self.VERTICAL_FORCE_SCALE

        # Bounce off ground
        if self.pos[1] >= GROUND_Y - self.radius:
            # Check if this is a significant bounce (ball was moving down with speed)
            significant_bounce = self.vel[1] > self.ground_collision_threshold
            
            # Position correction
            self.pos[1] = GROUND_Y - self.radius
            
            if self.special_effect_active:
                # Almost no bounce for special effect
                self.vel[1] *= -0.1 * self.VERTICAL_FORCE_SCALE # Minimal vertical bounce
                self.vel[0] *= 0.98 * self.HORIZONTAL_FORCE_SCALE # Keep almost all horizontal momentum
            else:
                # Normal bounce
                self.vel[1] *= self.bounciness * self.VERTICAL_FORCE_SCALE # Normal bounce
                self.vel[0] *= 0.99 * self.HORIZONTAL_FORCE_SCALE # Normal horizontal friction
                
                # Play sound if it's a significant bounce
                if significant_bounce:
                    play_sound('ball_ground')
                    
                    # Add collision flash for visualization in debug mode
                    if DEBUG_MODE:
                        self.collision_flash = 5

        # Bounce off walls (edges of the screen)
        if self.pos[0] <= self.radius:
            self.pos[0] = self.radius
            self.vel[0] *= -1 * self.HORIZONTAL_FORCE_SCALE
            play_sound('ball_ground')  # Use same sound for wall bounce
            
            # Add collision flash for visualization in debug mode
            if DEBUG_MODE:
                self.collision_flash = 5
                
        elif self.pos[0] >= WIDTH - self.radius:
            self.pos[0] = WIDTH - self.radius
            self.vel[0] *= -1 * self.HORIZONTAL_FORCE_SCALE
            play_sound('ball_ground')  # Use same sound for wall bounce
            
            # Add collision flash for visualization in debug mode
            if DEBUG_MODE:
                self.collision_flash = 5
                
        if player.rect.colliderect(self.get_rect()):
            if player.current_action == "kick":
                if player.is_flipped:
                    self.vel[0] = -10
                    self.vel[1] = -5
                else:
                    self.vel[0] = 10
                    self.vel[1] = -5
                    
        if bot.rect.colliderect(self.get_rect()):
            if bot.current_action == "kick" or bot.current_action == "attack":
                if bot.is_flipped:
                    self.vel[0] = -10
                    self.vel[1] = -5
                else:
                    self.vel[0] = 10
                    self.vel[1] = -5
            
        for rect in rects:
            collision_before = resolve_ball_obj_collision(self.pos, self.vel, self.radius, rect, bounce_factor=1)
            if collision_before and DEBUG_MODE:
                self.collision_flash = 5
        
        for player_object in player_objects:
            player_rect = player_object.rect  # Access the player's rectangle
            
            if isinstance(bot, BotLevel1):
                if bot.power_kick and player_object != bot:
                    # resolve_power_kick_collision(self, self.vel, player_rect)
                    bot_power_kick_player_ball_collision(
                        self.pos, self.vel, self.radius,
                        player, bounce_factor=0.5,
                        power_kick_strength=2,
                        player_push_strength=80
                    )
                else:
                    resolve_ball_player_collision(self.pos, self.vel, self.radius, player_rect, horizontal_bounce_factor=0.5, vertical_bounce_factor=0.8)
            else:
                resolve_ball_player_collision(self.pos, self.vel, self.radius, player_rect, horizontal_bounce_factor=0.5, vertical_bounce_factor=0.8)

        
        # Simulate rotational friction and update angle
        rotation_speed_factor = 2.0
        if self.special_effect_active:
            rotation_speed_factor = 3.0  # REDUCED from 4.0 to 3.0 for slower rotation
            
        self.rotation_speed = self.vel[0] * rotation_speed_factor *  self.HORIZONTAL_FORCE_SCALE
        self.rotation_speed *= 0.90  # decay factor
        self.angle += self.rotation_speed
        self.angle %= 360
        
        # Check if ball stopped moving - only end special effect if character animation not locked
        if abs(self.vel[0]) < 1e-4 and self.pos[1] == GROUND_Y - self.radius and (self.pos[0] <= 30 or self.pos[0] >= 720):
            # Only turn off effect if character not in animation
            if not (self.character_ref and hasattr(self.character_ref, 'animation_locked') and self.character_ref.animation_locked):
                self.special_effect_active = False  # Turn
                self.previous_positions = []  # Clear trail
                self.particles = []  # Clear particles
            return True
        
        # Check if ball out of bounds - only end special effect if character animation not locked
        if self.pos[0] <= 0 or self.pos[0] >= WIDTH:
            # Only turn off effect if character not in animation
            if not (self.character_ref and hasattr(self.character_ref, 'animation_locked') and self.character_ref.animation_locked):
                self.special_effect_active = False  # Turn off effect when ball goes out of bounds
                self.previous_positions = []  # Clear trail
                self.particles = []  # Clear particles
            return True
    
        return False
    
    def activate_special_effect(self, character_ref=None):
        if self.power_frames:  # Only activate if we have power frames loaded
            self.special_effect_active = True
            self.special_effect_timer = self.special_effect_duration
            self.power_frame_index = 0
            self.power_frame_counter = 0
            self.previous_positions = []  # Clear any existing trail
            self.particles = []  # Clear any existing particles
            self.pulse_timer = 0  # Reset pulse timer
            
            # Store the character reference if provided
            # Check if it's a PowerManager reference or character reference
            if character_ref:
                self.character_ref = character_ref
                # IMPORTANT: When special effect is activated, mark that character touched it
                self.set_last_touched(True)
                print("POWER SHOT: Ball kicked by CHARACTER")
            
            # Initial velocity vector modification for a low, direct shot
            speed = (self.vel[0]**2 * self.HORIZONTAL_FORCE_SCALE + self.vel[1]**2 * self.VERTICAL_FORCE_SCALE)**0.5
            if speed > 0:
                # Get the current direction as normalized vector
                dir_x = self.vel[0] / speed
                dir_y = self.vel[1] / speed
                
                # Calculate a more horizontal direction (reduce any upward component)
                # If the ball is moving upward (negative y velocity), reduce that component
                if dir_y < 0:
                    # Cancel out 80% of the upward motion
                    dir_y *= 0.2
                
                # Add a slight downward component to ensure a low shot
                dir_y += 0.1
                
                # Normalize the direction vector again
                dir_mag = math.sqrt(dir_x**2 + dir_y**2)
                dir_x /= dir_mag
                dir_y /= dir_mag
                
                # Apply a speed boost in this modified direction
                new_speed = speed * 1.8  
                self.vel[0] = dir_x * new_speed * self.HORIZONTAL_FORCE_SCALE
                self.vel[1] = dir_y * new_speed * self.VERTICAL_FORCE_SCALE
            else:
                # If ball isn't moving, give it a default horizontal direction
                self.vel[0] = 6.0 * self.HORIZONTAL_FORCE_SCALE# Moderate horizontal speed
                self.vel[1] = 1.0 * self.VERTICAL_FORCE_SCALE # Slight downward component
            
            # Very little bounce for more direct shots
            self.bounciness = -0.1  # Almost no bounce
            
            # Add initial burst of particles - INCREASED for more visible effect
            for _ in range(30):  # Increased from 20 to 30
                angle = random.uniform(0, 2 * 3.14159)
                speed = random.uniform(3, 10)  # Increased speed range
                particle = {
                    'pos': [self.pos[0], self.pos[1]],
                    'vel': [speed * math.cos(angle), speed * math.sin(angle)],
                    'radius': random.uniform(3, 8),  # Larger particles
                    'lifetime': random.randint(30, 60),  # Longer lifetime
                    'color': (random.randint(200, 255), 
                             random.randint(100, 255), 
                             random.randint(50, 150))
                }
                self.particles.append(particle)
        else:
            print("Cannot activate special effect: power frames not loaded")

    def draw(self, screen):
        # Draw particles first (behind everything)
        for particle in self.particles:
            alpha = min(255, int(255 * (particle['lifetime'] / 30.0)))
            color_with_alpha = (*particle['color'], alpha)
            
            # Create a surface for the particle with transparency
            particle_surface = pygame.Surface((int(particle['radius'] * 2), int(particle['radius'] * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, 
                            (int(particle['radius']), int(particle['radius'])), int(particle['radius']))
            
            screen.blit(particle_surface, 
                    (int(particle['pos'][0] - particle['radius']), 
                        int(particle['pos'][1] - particle['radius'])))
        
        # Draw trail segments ONLY (we'll skip drawing the main flame)
        if self.special_effect_active and self.power_frames:
            # Add pulsing effect for more visual impact
            self.pulse_timer += 1
            pulse_amount = math.sin(self.pulse_timer * 0.1) * 0.15 + 1.0  # 15% size oscillation
            
            # Draw the trail frames from oldest to newest
            for i, (pos_x, pos_y, frame_idx, trail_dir) in enumerate(self.previous_positions):
                if i < len(self.frame_opacity):  # Make sure we have opacity defined
                    # Get the frame
                    frame = self.power_frames[frame_idx]
                    
                    # Create a copy with alpha for trail effect
                    alpha_frame = frame.copy()
                    alpha_frame.set_alpha(self.frame_opacity[i])
                    
                    # Scale frames based on position in trail
                    scale_factor = 0.85 + (i / (len(self.previous_positions) * 1.0))  # INCREASED base scale
                    # Base size is 300
                    scaled_width = int(300 * scale_factor)
                    scaled_height = int(300 * scale_factor)
                    scaled_frame = pygame.transform.scale(alpha_frame, (scaled_width, scaled_height))
                    
                    # Rotate frame to match the ball's direction at that point
                    rotated_frame = pygame.transform.rotate(scaled_frame, -trail_dir)
                    
                    # Position the frame at the stored position
                    frame_x = pos_x - rotated_frame.get_width() // 2
                    frame_y = pos_y - rotated_frame.get_height() // 2
                    
                    # Draw the trail segment
                    screen.blit(rotated_frame, (frame_x, frame_y))
        
            # NOW draw the main flame at the ball's position (ONLY if we don't have enough trail segments yet)
            # This prevents duplicate flames when there's already a full trail
            if len(self.previous_positions) < self.max_trail_length:
                current_frame = self.power_frames[self.power_frame_index]
                
                # Apply pulsing effect to main flame
                pulse_width = int(current_frame.get_width() * pulse_amount)
                pulse_height = int(current_frame.get_height() * pulse_amount)
                pulsed_frame = pygame.transform.scale(current_frame, (pulse_width, pulse_height))
                
                # Always rotate the flame to match the ball's direction
                rotated_frame = pygame.transform.rotate(pulsed_frame, -self.direction)
                
                # Calculate the appropriate offset to align the right edge of the flame with the ball
                direction_rad = math.radians(self.direction)
                
                # MORE CENTERED: Reduced offset for more centered appearance
                offset_distance = rotated_frame.get_width() // 2 + 30  # Reduced from 90 to 30
                
                # Calculate x and y components of the offset
                offset_x = math.cos(direction_rad) * offset_distance
                offset_y = math.sin(direction_rad) * offset_distance
                
                # Position the frame with the calculated offset
                frame_x = self.pos[0] - rotated_frame.get_width() // 2 - offset_x
                frame_y = self.pos[1] - rotated_frame.get_height() // 2 - offset_y
                
                # Draw the rotated frame
                screen.blit(rotated_frame, (frame_x, frame_y))
        
        # Rotate the image and update position for the ball
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        rect = self.image.get_rect(center=(int(self.pos[0]), int(self.pos[1])))
        
        # Draw the actual ball (AFTER the effect so ball is on top)
        screen.blit(self.image, rect.topleft)
        
        # Draw collision flash if active
        if hasattr(self, 'collision_flash') and self.collision_flash > 0:
            flash_radius = self.radius + 5
            flash_alpha = int(255 * (self.collision_flash / 10))
            flash_surface = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (255, 255, 0, flash_alpha), 
                            (flash_radius, flash_radius), flash_radius)
            screen.blit(flash_surface, 
                    (int(self.pos[0] - flash_radius), int(self.pos[1] - flash_radius)))
            
        # Draw collision visualization if debug mode is enabled
        if DEBUG_MODE:
            # Draw collision circle
            pygame.draw.circle(screen, (0, 0, 255), 
                            (int(self.pos[0]), int(self.pos[1])), 
                            self.radius, 2)  # Blue circle outline
            
            # Label
            font = pygame.font.Font(None, 20)
            text = font.render("Ball", True, (0, 0, 255))
            screen.blit(text, (int(self.pos[0] - 15), int(self.pos[1] - self.radius - 20)))
            
            # Show velocity as an arrow
            if abs(self.vel[0]) > 0.1 or abs(self.vel[1]) > 0.1:
                vel_magnitude = math.sqrt(self.vel[0]**2 * self.HORIZONTAL_FORCE_SCALE + self.vel[1]**2 * self.VERTICAL_FORCE_SCALE)
                arrow_length = min(50, vel_magnitude * 5)  # Scale arrow but cap at 50px
                arrow_dir_x = self.vel[0] / vel_magnitude
                arrow_dir_y = self.vel[1] / vel_magnitude
                
                # Draw velocity arrow
                end_x = int(self.pos[0] + arrow_dir_x * arrow_length)
                end_y = int(self.pos[1] + arrow_dir_y * arrow_length)
                pygame.draw.line(screen, (255, 0, 0), 
                               (int(self.pos[0]), int(self.pos[1])), 
                               (end_x, end_y), 2)
                
                # Draw arrowhead
                arrowhead_size = 8
                angle = math.atan2(arrow_dir_y, arrow_dir_x)
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (end_x, end_y),
                    (int(end_x - arrowhead_size * math.cos(angle - math.pi/6)), 
                     int(end_y - arrowhead_size * math.sin(angle - math.pi/6))),
                    (int(end_x - arrowhead_size * math.cos(angle + math.pi/6)), 
                     int(end_y - arrowhead_size * math.sin(angle + math.pi/6)))
                ])
                
                # Show velocity text
                vel_text = font.render(f"Vel: ({self.vel[0]:.1f}, {self.vel[1]:.1f})", True, (255, 0, 0))
                screen.blit(vel_text, (int(self.pos[0] - 15), int(self.pos[1] - self.radius - 40)))

    def get_rect(self):
        return pygame.Rect(self.pos[0] - self.radius, self.pos[1] - self.radius, self.radius * 2, self.radius * 2)

    def reset(self):
        print("Ball reset called")
        # Don't reset if character is in locked animation
        if self.character_ref and hasattr(self.character_ref, 'animation_locked') and self.character_ref.animation_locked:
            return False
            
        # Save references we want to keep
        temp_power_frames = self.power_frames
        temp_arena = self.arena
        temp_original_power_frames = self.original_power_frames if hasattr(self, 'original_power_frames') else None
        temp_original_image = self.original_image
        
        # Reset to DEFAULT POSITION - SAME AS __init__
        self.pos = [WIDTH // 2, 100]  # This is the same as in __init__ - ball drops from sky
        self.vel = [0, 0]  # Stop all movement
        self.angle = 0
        self.bounciness = -0.8
        
        # Reset special effects
        self.special_effect_active = False
        self.special_effect_timer = 0
        self.character_ref = None
        
        # Reset particles and trails
        self.previous_positions = []
        self.particles = []
        
        # Reset animation properties
        self.power_frame_index = 0
        self.power_frame_counter = 0
        self.direction = 0
        self.pulse_timer = 0
        self.pulse_scale = 1.0
        
        # Reset touch tracking (changed from kick tracking)
        self.last_touch_timer = 0
        
        # Reset collision visualization
        self.collision_flash = 0
        
        # Restore references
        self.power_frames = temp_power_frames
        self.arena = temp_arena
        self.original_image = temp_original_image
        if temp_original_power_frames:
            self.original_power_frames = temp_original_power_frames
        
        print(f"Ball reset to default position (drops from sky): ({self.pos[0]}, {self.pos[1]})")
        return True
