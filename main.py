import pygame
import sys
import os
import time

# Initialize Pygame
pygame.init()

# Game Constants
TOTAL_TIME = 60  # seconds
football_net = pygame.image.load("images/goal/9-99121_soccer-goal-clipart-removebg-preview.png")


class CharacterAnimation:
    def __init__(self, idle_frames, run_frames, kick_frames, jump_frames):
        def load_images(frame_list, resize=(120, 200)):
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
        self.ball_last_kicked_by_character = False


        if not all([self.idle_animation, self.run_animation, self.kick_animation, self.jump_animation]):
            raise RuntimeError("One or more animations failed to load. Check file paths.")

        self.current_animation = self.idle_animation
        self.frame_index = 0
        self.frame_counter = 0
        self.frame_delay = 5
        self.is_jumping = False
        self.is_grounded = True
        self.jump_height = 0
        self.jump_speed = 10
        self.gravity = 2
        self.is_flipped = False  # Track direction
        self.position_x = 300  # Initial x position
        self.position_y = 300  # initial vertical position
        self.move_speed = 5  # Movement speed

    def draw_score(self):
        score_surface = self.score_font.render(f"Score: {self.score}", True, (0, 0, 0))
        score_rect = score_surface.get_rect(topleft=(20, 20))
        bg_rect = pygame.Rect(score_rect.left - 5, score_rect.top - 5, score_rect.width + 10, score_rect.height + 10)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        self.screen.blit(score_surface, score_rect)
    


    def update(self,keys_pressed):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.current_animation)

        if self.is_jumping:
            if self.jump_height < 50:
                self.jump_height += self.jump_speed
            else:
                self.is_jumping = False
        else:
            if self.jump_height > 0:
                self.jump_height -= self.gravity
            else:
                self.jump_height = 0
                self.is_grounded = True
            # Handle movement (left and right)
        if pygame.K_a in keys_pressed:
            self.position_x -= self.move_speed
            self.is_flipped = True
        if pygame.K_d in keys_pressed:
            self.position_x += self.move_speed
            self.is_flipped = False
 
        # Ensure the character stays within screen bounds
        self.position_x = max(0, min(800 - 120, self.position_x))  # 120 is character width
        self.position_y = max(0, min(600 - 200, self.position_y))  # 200 is character height
    

    def set_animation(self, action):
        if action == "idle":
            self.current_animation = self.idle_animation
        elif action == "run":
            self.current_animation = self.run_animation
        elif action == "kick":
            self.current_animation = self.kick_animation
        elif action == "jump" and self.is_grounded:
            self.current_animation = self.jump_animation
            self.is_jumping = True
            self.is_grounded = False
        self.frame_index = 0

    def draw(self, surface, x, y):
        img = self.current_animation[self.frame_index]
        if self.is_flipped:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, (x, y - self.jump_height))
        


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
        pygame.display.set_caption("Simple Soccer Game")
        self.football_net_img = pygame.image.load("images/goal/9-99121_soccer-goal-clipart-removebg-preview.png")
        self.football_net_img = pygame.transform.scale(self.football_net_img, (200, 200))

        self.left_net_rect = pygame.Rect(0, 350, 200, 200)     # Left side
        self.right_net_rect = pygame.Rect(600, 350, 200, 200)  # Right side

         # Load football
        self.football_img = pygame.image.load("images/ball/foodballpng-removebg-preview.png")
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

            # Load character animations
        base_path = "images" 

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



        
        # Move ball if it has velocity
        if abs(self.football_velocity) > 0:
            self.football_pos[0] += self.football_velocity

            # Add basic friction
            if self.football_velocity > 0:
                self.football_velocity -= 0.2
                if self.football_velocity < 0:
                    self.football_velocity = 0
            elif self.football_velocity < 0:
                self.football_velocity += 0.2
                if self.football_velocity > 0:
                    self.football_velocity = 0
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
 
    def run(self):
        running = True
        while running:
            running = self.handle_events()  # Handle events and user input
            self.update()  # Update game state
            self.draw()  # Draw game elements
            self.clock.tick(60)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()


pygame.quit()
sys.exit()
