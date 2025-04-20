import pygame
import sys
import os

from config import *

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Simple Soccer Game")
clock = pygame.time.Clock()

# Game elements (create objects)


# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

    class CharacterAnimation:
    def __init__(self, idle_frames, run_frames, kick_frames, jump_frames):
        def load_images(frame_list, resize=(IMAGE_WIDTH, IMAGE_HEIGHT)):
            loaded_images = []
            for frame in frame_list:
                try:
                    img = pygame.image.load(frame)
                    img = pygame.transform.scale(img, resize)
                    loaded_images.append(img)
                except pygame.error:
                    print(f"❌ Error: Could not load image {frame}")
            return loaded_images

        self.idle_animation = load_images(idle_frames)
        self.run_animation = load_images(run_frames)
        self.kick_animation = load_images(kick_frames)
        self.jump_animation = load_images(jump_frames)

        if not all([self.idle_animation, self.run_animation, self.kick_animation, self.jump_animation]):
            raise RuntimeError("One or more animations failed to load. Check file paths.")

        self.current_animation = self.idle_animation  # Default to idle
        self.frame_index = 0
        self.frame_counter = 0
        self.frame_delay = 5
        self.is_jumping = False
        self.is_grounded = True  # Character starts on the ground
        self.jump_height = 0
        self.jump_speed = 10
        self.gravity = 2
        self.is_flipped = False  # Track direction

    def update(self):
        """Update animation frames and handle jump physics."""
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)  # Loop animation

        # Handle Jumping Animation
        if self.is_jumping:
            if self.jump_height < 50:  # Move up
                self.jump_height += self.jump_speed
            else:
                self.is_jumping = False  # Reached peak, start falling
        else:
            if self.jump_height > 0:  # Falling back down
                self.jump_height -= self.gravity
            else:
                self.jump_height = 0
                self.is_grounded = True  # Landed on the ground

    def set_animation(self, action):
        """Switch animation based on action."""
        if action == "idle":
            self.current_animation = self.idle_animation
        elif action == "run":
            self.current_animation = self.run_animation
        elif action == "kick":
            self.current_animation = self.kick_animation
        elif action == "jump" and self.is_grounded:  # Only allow jumping if on ground
            self.current_animation = self.jump_animation
            self.is_jumping = True
            self.is_grounded = False  # Mid-air

        self.frame_index = 0  # Reset frame index to avoid out-of-range error

    def draw(self, surface, x, y):
        """Draw the character, adjusting position for jump height and flipping if needed."""
        img = self.current_animation[self.frame_index]
        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)  # Flip horizontally
        surface.blit(img, (x, y - self.jump_height))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Character Animation Example")
        
        # Get the user directory dynamically
        user_directory = os.path.expanduser("~")
        
        # Construct paths dynamically
        self.idle_frames = [os.path.join(user_directory, 'OneDrive - Asia Pacific University of Technology And Innovation (APU)', 
                                         'Desktop', 'ISE', 'ISE assignment', 'character', 'idle', f'Idle A-{str(i).zfill(2)}.png') for i in range(1, 7)]
        self.run_frames = [os.path.join(user_directory, 'OneDrive - Asia Pacific University of Technology And Innovation (APU)', 
                                        'Desktop', 'ISE', 'ISE assignment', 'character', 'Run', f'Run A-{str(i).zfill(2)}.png') for i in range(1, 9)]
        self.kick_frames = [
            os.path.join(user_directory, 'OneDrive - Asia Pacific University of Technology And Innovation (APU)', 
                         'Desktop', 'ISE', 'ISE assignment', 'character', 'kick', 'Attack A-03.png'),
            os.path.join(user_directory, 'OneDrive - Asia Pacific University of Technology And Innovation (APU)', 
                         'Desktop', 'ISE', 'ISE assignment', 'character', 'kick', 'Attack A-04.png')
        ]
        self.jump_frames = [os.path.join(user_directory, 'OneDrive - Asia Pacific University of Technology And Innovation (APU)', 
                                         'Desktop', 'ISE', 'ISE assignment', 'character', 'jump', f'Jump A-{str(i).zfill(2)}.png') for i in range(1, 11)]

        # Create character animation object
        self.character = CharacterAnimation(self.idle_frames, self.run_frames, self.kick_frames, self.jump_frames)
        self.current_action = "idle"
        self.keys_pressed = set()

    def handle_events(self):
        """Handle all user input and update the character's action."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)  # Track pressed keys
                if event.key == pygame.K_k:  # Press 'K' to kick
                    self.current_action = "kick"
                elif event.key == pygame.K_SPACE:  # Press 'J' to jump (only if on ground)
                    if self.character.is_grounded:
                        self.current_action = "jump"  # Set current_action to "jump"
                elif event.key == pygame.K_d:  # Press 'D' to run
                    self.current_action = "run"
                    self.character.is_flipped = False  # Face right
                elif event.key == pygame.K_a:  # Press 'A' to run left
                    self.current_action = "run"
                    self.character.is_flipped = True  # Face left
                self.character.set_animation(self.current_action)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                if event.key in [pygame.K_k, pygame.K_SPACE, pygame.K_d, pygame.K_a]:
                    if not self.keys_pressed:
                        self.current_action = "idle"
                        self.character.set_animation(self.current_action)

        return True

    def update(self):
        """Update the game state (animations, physics)."""
        self.character.update()

    def draw(self):
        """Draw everything on the screen.""" 
        self.screen.fill((30, 30, 30))  # Background color
        self.character.draw(self.screen, 300, 300)  # Draw the character
        pygame.display.update()  # Update the display

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_events()  # Handle events and user input
            self.update()  # Update game state
            self.draw()  # Draw game elements
            pygame.time.delay(30)  # Smooth transition


def main():
    game = Game()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()




    
    # Get player inputs
    keys = pygame.key.get_pressed()
    
    # Player handle input


    # Update game state for player
    
    
    # Update game state for bot
    
    
    # Update game state for ball
    
    
    # Handle collisions after all positions are updated


    # Update scoreboard
    

    # Draw goal post


    # Draw game elements


    # Update display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
