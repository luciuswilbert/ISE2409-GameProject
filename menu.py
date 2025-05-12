import pygame
import sys
from config import *
from sound_manager import play_sound, stop_sound, stop_all_sounds

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load background image
        try:
            self.background_img = pygame.image.load("images/background/menu_background.png").convert()
            self.background_img = pygame.transform.scale(self.background_img, (WIDTH, HEIGHT))
        except pygame.error:
            print("Error loading menu background image. Using solid color instead.")
            self.background_img = None
        
        # Load fonts
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.message_font = pygame.font.Font(None, 48)
        
        # Load button image
        try:
            self.start_button_img = pygame.image.load("images/button/play_button.png").convert_alpha()
            self.retry_button_img = pygame.image.load("images/button/replay.png").convert_alpha()
            self.start_button_img = pygame.transform.scale(self.start_button_img, (200, 80))
            self.retry_button_img = pygame.transform.scale(self.retry_button_img, (200, 80))
            self.start_button_rect = self.start_button_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
            self.retry_button_rect = self.retry_button_img.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        except:
            print("Error loading button image. Using rectangle instead.")
            self.start_button_img = None
            self.retry_button_img = None
            self.start_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 80)
            self.retry_button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 80)
        
        # Colors - Define colors directly with RGB tuples
        self.title_color = (255, 215, 0)     # Gold color for title
        self.message_color = (255, 0, 0)     # Red for error messages
        self.button_color = (50, 150, 250)   # Blue for buttons
        self.button_hover_color = (70, 170, 270)  # Lighter blue for hover
        self.white = (255, 255, 255)         # White for text
        self.black = (0, 0, 0)               # Black for background
    
    def run(self):
        """Run the main menu"""
        self.running = True  # Reset running state
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

    def show_retry_menu(self):
        """Show the retry menu after losing the game"""
        self.running = True  # Reset running state
        play_sound('retry')
        while self.running:
            self.handle_events()
            self.draw_retry_menu()
            self.clock.tick(FPS)
        
    def handle_events(self):
        """Handle events for both main menu and retry menu"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.start_button_rect.collidepoint(mouse_pos):
                        print("Start button clicked")
                        # Stop the menu sound when start button is clicked
                        stop_sound('menu_sound')
                        play_sound('start_button')
                        self.running = False   # Exit menu and start game
                    if self.retry_button_rect.collidepoint(mouse_pos):
                        print("Retry button clicked")
                        # Stop the menu sound when retry button is clicked
                        stop_sound('menu_sound')
                        play_sound('start_button')
                        self.running = False
                        
    def draw(self):
        """Draw the main menu"""
        # Draw background image or fill with color
        if self.background_img:
            self.screen.blit(self.background_img, (0, 0))
        else:
            # Fill background with solid color as fallback
            self.screen.fill(self.black)
        
        # Create a semi-transparent overlay for better text readability
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        
        # Draw start button
        if self.start_button_img:
            self.screen.blit(self.start_button_img, self.start_button_rect)
            
            # Add hover effect
            if self.start_button_rect.collidepoint(pygame.mouse.get_pos()):
                # Create a semi-transparent overlay for hover effect
                s = pygame.Surface((self.start_button_rect.width, self.start_button_rect.height), pygame.SRCALPHA)
                s.fill((255, 255, 255, 50))  # White with 50 alpha
                self.screen.blit(s, self.start_button_rect)
        else:
            # Fallback rectangle button if image loading failed
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.start_button_rect.collidepoint(mouse_pos)
            button_color = self.button_hover_color if is_hovering else self.button_color
            
            # Draw button rectangle
            pygame.draw.rect(self.screen, button_color, self.start_button_rect, border_radius=10)
            
            # Draw button text
            button_text = self.button_font.render("START", True, self.white)
            button_text_rect = button_text.get_rect(center=self.start_button_rect.center)
            self.screen.blit(button_text, button_text_rect)

        pygame.display.flip()

    def draw_retry_menu(self):
        """Draw the retry menu after losing"""
        # Draw background image or fill with color
        if self.background_img:
            self.screen.blit(self.background_img, (0, 0))
        else:
            # Fill background with solid color as fallback
            self.screen.fill(self.black)
        
        # Create semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Darker semi-transparent black for retry menu
        self.screen.blit(overlay, (0, 0))
        
        # Draw lose message
        message_text = self.message_font.render("You lose! Please try again", True, self.message_color)
        message_rect = message_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(message_text, message_rect)
        
        # Draw retry button
        if self.retry_button_img:
            self.screen.blit(self.retry_button_img, self.retry_button_rect)
            
            # Add hover effect
            if self.retry_button_rect.collidepoint(pygame.mouse.get_pos()):
                s = pygame.Surface((self.retry_button_rect.width, self.retry_button_rect.height), pygame.SRCALPHA)
                s.fill((255, 255, 255, 50))
                self.screen.blit(s, self.retry_button_rect)
        else:
            # Fallback rectangle button
            mouse_pos = pygame.mouse.get_pos()
            is_hovering = self.retry_button_rect.collidepoint(mouse_pos)
            button_color = self.button_hover_color if is_hovering else self.button_color
            
            # Draw button rectangle
            pygame.draw.rect(self.screen, button_color, self.retry_button_rect, border_radius=10)
            
            # Draw button text
            button_text = self.button_font.render("RETRY", True, self.white)
            button_text_rect = button_text.get_rect(center=self.retry_button_rect.center)
            self.screen.blit(button_text, button_text_rect)        
        
        pygame.display.flip()