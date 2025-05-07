import pygame
import time
import sys
from config import TOTAL_TIME

class Arena:
    def __init__(self):
        # load Background
        self.background_img_raw = pygame.image.load("images/background/fire_animatiaon.gif")
        self.background_img = pygame.transform.scale(self.background_img_raw, (800, 600))
        
        # Load Goal
        self.football_net_img = pygame.image.load("images/goal/9-99121_soccer-goal-clipart-removebg-preview.png")
        self.football_net_img = pygame.transform.scale(self.football_net_img, (100, 250))
        self.left_net_rect = pygame.Rect(0, 350, 100, 250)     # Left side
        self.right_net_rect = pygame.Rect(700, 350, 100, 250)  # Right side
        self.left_net_rect_goal_area = pygame.Rect(30, 395, 50, 150)
        self.right_net_rect_goal_area = pygame.Rect(720, 395, 50, 150)
        self.left_net_rect_top_bar = pygame.Rect(30, 380, 50, 15)
        self.left_net_rect_side_bar = pygame.Rect(0, 380, 30, 165)
        self.right_net_rect_top_bar = pygame.Rect(720, 380, 50, 15)
        self.right_net_rect_side_bar = pygame.Rect(770, 380, 30, 165)
        
        # Load font and setup timer
        self.start_time = time.time()
        self.total_time = TOTAL_TIME
        self.font = pygame.font.Font(None, 36)
        
        # Initialize score
        self.score = 0
        self.score_font = pygame.font.Font(None, 48)
        self.celebrating = False
        self.celebration_start_time = None
        self.celebration_duration_sec = 3  # seconds
        self.clock = pygame.time.Clock()
        self.ball_last_kicked_by_character = True

    def draw_timer(self, screen):
        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.total_time - elapsed)
        timer_surface = self.font.render(f"Time: {remaining}", True, (0, 0, 0))
        timer_rect = timer_surface.get_rect(topright=(800 - 20, 20))
        bg_rect = pygame.Rect(timer_rect.left - 5, timer_rect.top - 5, timer_rect.width + 10, timer_rect.height + 10)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        screen.blit(timer_surface, timer_rect)

        if remaining <= 0:
            print("⏰ Time's up!")
            pygame.time.wait(2000)
            pygame.quit()
            sys.exit()
            
    def draw_score(self, screen):
        score_surface = self.score_font.render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(20, 20))
        bg_rect = pygame.Rect(score_rect.left - 5, score_rect.top - 5, score_rect.width + 10, score_rect.height + 10)
        pygame.draw.rect(screen, (255, 255, 255), bg_rect)
        screen.blit(score_surface, score_rect)
    
    def update_score(self, ball_rect):
        if self.left_net_rect_goal_area.contains(ball_rect) or self.right_net_rect_goal_area.contains(ball_rect):
            if self.ball_last_kicked_by_character and not self.celebrating:
                self.score += 1
                print("GOAL! 🎯 Score:", self.score)
                self.celebrating = True
                self.celebration_start_time = time.time()
                return True  # Indicate goal scored
        return False


    def draw(self, screen, ball, character, bot):
        flipped_left_net = pygame.transform.flip(self.football_net_img, True, False)

        screen.blit(self.background_img, (0, 0))
        screen.blit(flipped_left_net, self.left_net_rect.topleft) # Left net
        screen.blit(self.football_net_img, self.right_net_rect.topleft)  # Right net
        # pygame.draw.rect(screen, (255, 0, 0), self.left_net_rect, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.right_net_rect, 2)
        
        # # Draw first rectangle (e.g., red, filled)
        # pygame.draw.rect(screen, (255, 0, 0), self.left_net_rect_top_bar, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.left_net_rect_side_bar, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.right_net_rect_top_bar, 2)
        # pygame.draw.rect(screen, (255, 0, 0), self.right_net_rect_side_bar, 2)

        # # Draw second rectangle (e.g., green, outlined)
        # pygame.draw.rect(screen, (0, 255, 0), self.left_net_rect_goal_area, 2)
        # pygame.draw.rect(screen, (0, 255, 0), self.right_net_rect_goal_area, 2)
    
        self.draw_timer(screen)
        self.draw_score(screen)
        
        ball.draw(screen)
        character.draw(screen)
        bot.draw(screen)

        if self.celebrating:
            font = pygame.font.SysFont(None, 100)
            goal_text = font.render("GOAL!", True, (255, 215, 0))  # Gold
            screen.blit(goal_text, (400 - goal_text.get_width() // 2, 250))
            pygame.display.update()
            
            # Freeze the game briefly
            pygame.time.delay(1000)  # 2 seconds
            self.ball_last_kicked_by_character = True
            self.celebrating = False
            
            return  # Skip rest of the draw logic