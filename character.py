import pygame

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