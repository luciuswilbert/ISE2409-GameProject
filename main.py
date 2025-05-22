import pygame
import sys
import pygame.mixer
from story import *

import arena
from config import *
from gameLevel1 import GameLevel1
from gameLevel2 import GameLevel2
from menu import Menu  # Import the Menu class
from sound_manager import initialize_sounds, play_sound


class MainGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()

        # Initialize sounds
        initialize_sounds()
        
        # Screen setup
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Legends of OrbArena")
        
        # Game state
        self.running = True
        self.current_state = "MENU"  # MENU, PLAYING, GAME_OVER
        self.current_level = 2
        self.max_levels = 2  # Currently have 2 levels
        
        # Create menu instance
        self.menu = Menu(self.screen)
        
    # In MainGame class in main.py
    def show_main_menu(self):
        """Display the main menu using the Menu class"""
        from sound_manager import play_sound, stop_sound
        
        # Play menu sound
        play_sound('menu_sound', loop=True)
        
        self.menu.running = True
        self.menu.run()
        
        # Menu already handles stopping the sound on button clicks,
        # so we don't need to stop it here again
        if not self.menu.running:
            self.current_state = "PLAYING"
            self.current_level = 1  # Always start at level 1
            
    def show_ready_start_transition(self):
        """Show 'Ready?' and 'Start!' captions before starting gameplay"""
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 120)  # Large font for visibility
        
        # Create a black background instead of capturing the current screen
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((0, 0, 0))  # Fill with black
        
        # First show "Ready?" caption
        ready_text = font.render("Ready?", True, (255, 255, 255))
        ready_rect = ready_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # Fade in "Ready?" text
        for alpha in range(0, 255, 5):
            # Use black background
            self.screen.blit(background, (0, 0))
            
            # Create a transparent surface for the text
            text_surface = pygame.Surface((ready_rect.width, ready_rect.height), pygame.SRCALPHA)
            ready_text_copy = ready_text.copy()
            ready_text_copy.set_alpha(alpha)
            text_surface.blit(ready_text_copy, (0, 0))
            
            # Overlay the text
            self.screen.blit(text_surface, ready_rect)
            pygame.display.flip()
            clock.tick(60)
        
        # Display "Ready?" for 1.5 seconds
        pygame.time.delay(1500)
        
        # Fade out "Ready?" text
        for alpha in range(255, 0, -5):
            # Use black background
            self.screen.blit(background, (0, 0))
            
            # Create a transparent surface for the text
            text_surface = pygame.Surface((ready_rect.width, ready_rect.height), pygame.SRCALPHA)
            ready_text_copy = ready_text.copy()
            ready_text_copy.set_alpha(alpha)
            text_surface.blit(ready_text_copy, (0, 0))
            
            # Overlay the text
            self.screen.blit(text_surface, ready_rect)
            pygame.display.flip()
            clock.tick(60)
        
        # Short pause
        pygame.time.delay(500)
        
        # Now show "Start!" caption
        start_text = font.render("Start!", True, (255, 255, 0))  # Yellow color for emphasis
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        
        # Fade in "Start!" text with a slight zoom effect
        for i in range(60):
            # Use black background
            self.screen.blit(background, (0, 0))
            
            scale = 0.5 + (i / 60) * 0.5  # Scale from 0.5 to 1.0
            scaled_text = pygame.transform.scale(
                start_text, 
                (int(start_rect.width * scale), int(start_rect.height * scale))
            )
            scaled_rect = scaled_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            # Overlay the scaled text
            self.screen.blit(scaled_text, scaled_rect)
            pygame.display.flip()
            clock.tick(60)
        
    
    def show_level_complete(self, level_num):
        """Display a level complete screen before moving to next level"""
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 100)
        small_font = pygame.font.SysFont(None, 50)

        try:
            # Try loading the background image
            complete_bg = pygame.image.load("images/background/complate_level_background.png").convert()
            complete_bg = pygame.transform.scale(complete_bg, (WIDTH, HEIGHT))
        except pygame.error as e:
            print(f"Error loading background image: {e}")
            complete_bg = None

        complete_bg = pygame.image.load("images/background/complate_level_background.png")
        complete_bg = pygame.transform.scale(complete_bg, (WIDTH, HEIGHT))

        
        # Play a victory sound
        play_sound('win')  # Use an existing sound for level complete
        
        waiting = True
        wait_timer = 0
        max_wait_time = 3 * FPS  # Auto-continue after 3 seconds
        
        while waiting and self.running and wait_timer < max_wait_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    waiting = False  # Any key press skips the screen
            
            # Draw level complete screen
            if complete_bg:
                self.screen.blit(complete_bg, (0, 0))  # Draw background first
            else:
                self.screen.fill((0, 0, 0)) 
            
            # Level complete text
            text = font.render(f"Level {level_num} Complete!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, text_rect)
            
            # Show next level text
            next_level_text = small_font.render(f"Get Ready for Level {level_num + 1}", True, (255, 255, 255))
            next_level_rect = next_level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(next_level_text, next_level_rect)
            
            # Continue prompt
            continue_text = small_font.render("Press any key to continue", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            
            # Make text pulse for visibility
            if (wait_timer // 15) % 2:  # Pulse every 15 frames
                self.screen.blit(continue_text, continue_rect)
            
            pygame.display.flip()
            clock.tick(FPS)
            wait_timer += 1
    
    def show_game_over(self, win):
        """Display game over screen - now using the Menu class for retry"""
        if not win:
            # Play menu sound for retry menu
            from sound_manager import play_sound

            # Use the retry menu from Menu class
            self.menu.running = True
            self.menu.show_retry_menu()
            
            # If retry button clicked, restart the game
            if not self.menu.running:
                self.current_state = "PLAYING"
                # self.current_level = 1
        else:
            # Show win screen (you could create a similar method in Menu class)
            # self.show_win_screen()
            # Story outro
            throne_room_dialogue_after(self.screen)
            # Show win screen (you could create a similar method in Menu class)
            self.show_win_screen()
    
    def show_win_screen(self):
        """Display win screen"""
        # Play menu sound for win screen
        from sound_manager import play_sound, stop_sound
        play_sound('win')
        
        clock = pygame.time.Clock()
        font = pygame.font.SysFont(None, 100)
        small_font = pygame.font.SysFont(None, 50)
        
        waiting = True
        while waiting and self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop_sound('menu_sound')  # Stop sound when quitting
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop_sound('menu_sound')  # Stop sound when ESC is pressed
                        self.running = False
                        waiting = False
                    elif event.key == pygame.K_m:
                        stop_sound('menu_sound')  # Stop sound when M is pressed
                        self.current_state = "MENU"
                        waiting = False
        
            # Draw win screen
            try:
                win_bg = pygame.image.load("images/background/complate_level_background.png").convert()
                win_bg = pygame.transform.scale(win_bg, (WIDTH, HEIGHT))
                self.screen.blit(win_bg, (0, 0))
            except pygame.error as e:
                print(f"Error loading win background: {e}")
                self.screen.fill((0, 0, 0))
            
            # Result text
            text = font.render("To Be Continued", True, (255, 215, 0))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            self.screen.blit(text, text_rect)
            
            menu_text = small_font.render("Press M for Main Menu", True, (255, 255, 255))
            menu_rect = menu_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
            self.screen.blit(menu_text, menu_rect)
            stop_sound('background')
            
            
            pygame.display.flip()
            clock.tick(FPS)
    
    def play_level(self):
        """Play the current level with progression"""
        last_result = False  # Store result for game over screen
        
        # Play through levels in sequence until player loses or completes all levels
        while self.current_level <= self.max_levels and self.running:
            if self.current_level == 1:
                result = GameLevel1(self.screen)
            elif self.current_level == 2:
                result = GameLevel2(self.screen)
            else:
                break  # No more levels
                1
            last_result = result  # Store result for game over screen
            
            if result:  # If player won the level
                if self.current_level < self.max_levels:
                    # Show level complete screen before moving to next level
                    self.show_level_complete(self.current_level)
                    # Move to next level
                    self.current_level += 1
                    self.current_state = "LEVEL_2_TRANSITION"  # Transition to level 2
                else:
                    # Player beat the final level
                    break
            else:
                # Player lost
                break
        
        # Game over when all levels are complete or player lost
        self.current_state = "GAME_OVER"
        self.show_game_over(last_result)
    
    def run(self):
        """Main game loop"""
        while self.running:
            if self.current_state == "MENU":
                self.show_main_menu()
                # Start menu and story intro
                play_first_video(self.screen)
                play_intro_scene(self.screen)
                self.screen.fill((0, 0, 0))
                pygame.display.flip()
                pygame.time.delay(200)
                self.show_ready_start_transition()
            elif self.current_state == "LEVEL_2_TRANSITION":
                self.level_2_transition()
            elif self.current_state == "PLAYING":
                self.play_level()
            elif self.current_state == "GAME_OVER":
                # This is handled in play_level
                pass
        
        pygame.quit()
        sys.exit()
        
    def level_2_transition(self):
        """Transition to level 2"""
        # Load the transition background
        transition_bg = pygame.image.load("images/background/fire_animatiaon.gif")
        transition_bg = pygame.transform.scale(transition_bg, (WIDTH, HEIGHT))
        # play the shake
        screen_shake_effect(self.screen, transition_bg)
        pygame.mixer.init()
        pygame.mixer.music.load("TransitionLv1Lv2/goingToCastle.mp3")  # replace with your path
        pygame.mixer.music.play()

        castle_zoom_out(self.screen, "TransitionLv1Lv2/CastleScene.png", duration_ms=12000)
        fade_to_black(self.screen, duration=1000)
        pygame.mixer.music.stop()

        gate_entry_scene(self.screen, "TransitionLv1Lv2/castle.png")

        throne_room_scene(self.screen)

        throne_room_dialogue(self.screen)
        
        self.show_ready_start_transition()
        
        self.current_state = "PLAYING"
        

# Main entry point
if __name__ == "__main__":
    game = MainGame()
    game.run()