import pygame
import time
from config import TOTAL_TIME
from character import CharacterAnimation
import sys

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
        pygame.display.set_caption("Simple Soccer Game")
        self.football_net_img = pygame.image.load("images/goal/9-99121_soccer-goal-clipart-removebg-preview.png")
        self.football_net_img = pygame.transform.scale(self.football_net_img, (200, 200))

        self.left_net_rect = pygame.Rect(0, 350, 200, 200)     # Left side
        self.right_net_rect = pygame.Rect(600, 350, 200, 200)  # Right side

         # Load football
        self.football_img = pygame.image.load("images/ball/ball.png")
        self.football_img = pygame.transform.scale(self.football_img, (50, 50))
        self.football_pos = [400, 400]
        self.football_velocity = 0  # 0 means stationary
        self.score = 0
        self.score_font = pygame.font.Font(None, 48)
        self.celebrating = False
        self.celebration_start_time = None
        self.celebration_duration_sec = 3  # seconds
        self.clock = pygame.time.Clock()

        # Load background image and scale
        self.background_img_raw = pygame.image.load("images/background/fire_animatiaon.gif")
        self.background_img = pygame.transform.scale(self.background_img_raw, (800, 600))

        # Load font and setup timer
        self.start_time = time.time()
        self.total_time = TOTAL_TIME
        self.font = pygame.font.Font(None, 36)

        self.idle_frames = [f'images/player/Idle A-{str(i).zfill(2)}.png' for i in range(1, 7)]
        self.run_frames = [f'images/player/Run A-{str(i).zfill(2)}.png' for i in range(1, 9)]
        self.kick_frames = ['images/player/Attack A-03.png', 'images/player/Attack A-04.png' ]
        self.jump_frames = [f'images/player/Jump A-{str(i).zfill(2)}.png' for i in range(1, 11)]

        self.character = CharacterAnimation(self.idle_frames, self.run_frames, self.kick_frames, self.jump_frames)
        self.current_action = "idle"
        self.keys_pressed = set()
        
    def draw_score(self):
        score_surface = self.score_font.render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(20, 20))
        bg_rect = pygame.Rect(score_rect.left - 5, score_rect.top - 5, score_rect.width + 10, score_rect.height + 10)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        self.screen.blit(score_surface, score_rect)


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                if event.key == pygame.K_k:
                    self.current_action = "kick"
                elif event.key == pygame.K_SPACE and self.character.is_grounded:
                    self.current_action = "jump"
                elif event.key in [pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s]:
                    self.current_action = "run"
                self.character.set_animation(self.current_action)

            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                if not self.keys_pressed:
                    self.current_action = "idle"
                    self.character.set_animation(self.current_action)
        return True


    def update(self):
        self.character.update(self.keys_pressed)
                # Check collision with ball (simple rectangle overlap)
        character_rect = pygame.Rect(
            self.character.position_x, self.character.position_y - self.character.jump_height, 120, 200
        )
        football_rect = pygame.Rect(self.football_pos[0], self.football_pos[1], 50, 50)
        football_rect = pygame.Rect(self.football_pos[0], self.football_pos[1], 50, 50)


        if character_rect.colliderect(football_rect):
            if self.current_action == "kick":
                if self.character.is_flipped:
                    self.football_velocity = -5
                else:
                    self.football_velocity = 5
                self.ball_last_kicked_by_character = True


        
        # # Move ball if it has velocity
        # if abs(self.football_velocity) > 0:
        #     self.football_pos[0] += self.football_velocity

        #     # Add basic friction
        #     if self.football_velocity > 0:
        #         self.football_velocity -= 0.2
        #         if self.football_velocity < 0:
        #             self.football_velocity = 0
        #     elif self.football_velocity < 0:
        #         self.football_velocity += 0.2
        #         if self.football_velocity > 0:
        #             self.football_velocity = 0
            # Stop ball if it goes out of bounds
            if self.left_net_rect.contains(football_rect) or self.right_net_rect.contains(football_rect):
               if self.ball_last_kicked_by_character and not self.celebrating:
                    self.score += 1
                    print("GOAL! 🎯 Score:", self.score)
                    self.celebrating = True
                    self.celebration_start_time = time.time()
                    self.football_velocity = 0
                    self.ball_last_kicked_by_character = False


            if self.celebrating:
                if time.time() - self.celebration_start_time >= self.celebration_duration_sec:
                    self.celebrating = False
                    self.football_pos = [400, 400]
                    self.character.position_x = 300
                    self.character.position_y = 300
                return  # Skip rest of update while celebrating


                    



    def draw_timer(self):
        elapsed = int(time.time() - self.start_time)
        remaining = max(0, self.total_time - elapsed)
        timer_surface = self.font.render(f"Time: {remaining}", True, (0, 0, 0))
        timer_rect = timer_surface.get_rect(topright=(800 - 20, 20))
        bg_rect = pygame.Rect(timer_rect.left - 5, timer_rect.top - 5, timer_rect.width + 10, timer_rect.height + 10)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        self.screen.blit(timer_surface, timer_rect)

        if remaining <= 0:
            print("⏰ Time's up!")
            pygame.time.wait(2000)
            pygame.quit()
            sys.exit()


    def draw(self): 
        self.screen.blit(self.background_img, (0, 0))  # Draw background
        self.screen.blit(self.football_img, self.football_pos)  # Ball
        self.character.draw(self.screen, self.character.position_x, self.character.position_y)

        flipped_left_net = pygame.transform.flip(self.football_net_img, True, False)
        self.screen.blit(flipped_left_net, self.left_net_rect.topleft)
        self.screen.blit(self.football_net_img, self.right_net_rect.topleft)  # Right net

        self.draw_timer()
        self.draw_score()
        if self.celebrating:
            font = pygame.font.SysFont(None, 100)
            goal_text = font.render("GOAL!", True, (255, 215, 0))  # Gold
            self.screen.blit(goal_text, (400 - goal_text.get_width() // 2, 200))
            pygame.display.update()
            
            # Freeze the game briefly
            pygame.time.delay(2000)  # 2 seconds
            self.celebrating = False
            self.football_pos = [400, 400]
            self.character.position_x = 300
            self.character.position_y = 300
            return  # Skip rest of the draw logic
        pygame.display.update()
 
    # def run(self):
    #     running = True
    #     while running:
    #         running = self.handle_events()  # Handle events and user input
    #         self.update()  # Update game state
    #         self.draw()  # Draw game elements
    #         self.clock.tick(60)