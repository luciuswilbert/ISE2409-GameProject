import pygame
import sys
import random

from config import *
from gameLevel1 import GameLevel1
from gameLevel2 import GameLevel2
from storyscene.introscene1 import *
from character import *
from botLevel2 import BotLevel2 

# Initialize Pygame
pygame.init()
pygame.mixer.init()


# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Legends of Orbithra")

def screen_shake_effect(screen, background_img, duration_ms=5000, intensity=10):
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    fade_start = duration_ms - 1000  # start fade 1 second before end
    pygame.mixer.music.load("TransitionLv1Lv2/rumble.mp3")  # replace with your path
    pygame.mixer.music.play()
    

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start

        if elapsed >= duration_ms:
            break

        # Shake background for the first part
        dx = random.randint(-intensity, intensity)
        dy = random.randint(-intensity, intensity)
        screen.fill((0, 0, 0))
        screen.blit(background_img, (dx, dy))

        # Fade to black in last 1 second
        if elapsed >= fade_start:
            fade_alpha = int(255 * (elapsed - fade_start) / 1000)  # 0 → 255
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.set_alpha(fade_alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))

    # Fade to black
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.fill((0, 0, 0))  # fill instead of blit background
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.mixer.music.stop()

def castle_zoom_out(screen, image_path, duration_ms=10000):
    original_img = pygame.image.load(image_path).convert()
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    start_scale = 2.0
    end_scale = 1.5

    base_width = 800
    base_height = 400 

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        if elapsed > duration_ms:
            break

        t = elapsed / duration_ms
        current_scale = start_scale * (1 - t) + end_scale * t

        # Calculate scaled dimensions
        scaled_w = int(base_width * current_scale)
        scaled_h = int(base_height * current_scale)

        scaled_img = pygame.transform.smoothscale(original_img, (scaled_w, scaled_h))

        # Center it in the screen
        x = (WIDTH - scaled_w) // 2
        y = (HEIGHT - scaled_h) // 2

        screen.fill((0, 0, 0))
        screen.blit(scaled_img, (x, y))
        pygame.display.flip()
        clock.tick(60)

def fade_to_black(screen, duration=1000):
    clock = pygame.time.Clock()
    black_surface = pygame.Surface((WIDTH, HEIGHT))
    black_surface.fill((0, 0, 0))

    for alpha in range(0, 256, 10):
        black_surface.set_alpha(alpha)
        screen.blit(black_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.time.delay(duration)

def gate_entry_scene(screen, background_path):
    clock = pygame.time.Clock()

    # Load background
    background = pygame.image.load(background_path).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Create the character
    player = CharacterAnimation()
    player.position_x = 100
    player.position_y = 400
    player.set_animation()  # Default to idle

    gate_rect = pygame.Rect(385, 150, 30, 30)

    keys_pressed = set()

    running = True
    while running:
        keys_down = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys_down[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        moving = False

        if keys_down[pygame.K_a]:  # Left
            player.position_x -= player.move_speed
            player.is_flipped = True
            moving = True

        if keys_down[pygame.K_d]:  # Right
            player.position_x += player.move_speed
            player.is_flipped = False
            moving = True

        if keys_down[pygame.K_w]:  # Up
            player.position_y -= player.move_speed
            moving = True

        if keys_down[pygame.K_s]:  # Down
            player.position_y += player.move_speed
            moving = True

        # Handle animation
        if moving and player.current_action != "run":
            player.current_action = "run"
            player.set_animation()
        elif not moving and player.current_action != "idle":
            player.current_action = "idle"
            player.set_animation()

        # Update and draw
        player.position_x = max(30, min(WIDTH - 100, player.position_x))  # prevent left wall & right edge
        player.position_y = max(120, min(HEIGHT - 120, player.position_y))  # prevent going too high or too low
        player.update(keys_down)
        screen.blit(background, (0, 0))
        player.draw(screen)

        pygame.display.flip()
        
        clock.tick(60)

        if player.rect.colliderect(gate_rect):
            fade_to_black(screen, duration=1000)
            return
        
def throne_room_scene(screen):
    clock = pygame.time.Clock()

    pygame.mixer.music.load("storyscene/beforeLuciferSoundTrack.mp3")
    pygame.mixer.music.play(-1)  # -1 = loop forever

    background = pygame.image.load("images/background/throne room.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Use CharacterAnimation for player (same size/pose as in gate scene)
    player = CharacterAnimation()
    player.position_x = 100
    player.position_y = 400
    player.set_animation()

    bot = BotLevel2()
    bot.position_x = WIDTH - 220
    bot.position_y = 400
    bot.set_animation()
    bot.is_flipped = True 

    
    start_time = pygame.time.get_ticks()
    duration = 5000  # milliseconds

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if pygame.time.get_ticks() - start_time > duration:
            pygame.mixer.music.fadeout(1000)  # fade out in 1 second
            running = False


        screen.blit(background, (0, 0))
        player.update(set())  # Stay idle
        player.draw(screen)

        bot.update()
        bot.draw(screen)


        pygame.display.flip()
        clock.tick(60)

def throne_room_dialogue(screen):
    clock = pygame.time.Clock()

    pygame.mixer.music.load("storyscene/beforeLuciferSoundTrack.mp3")
    pygame.mixer.music.play(-1)  # -1 = loop forever

    background = pygame.image.load("images/background/throne room.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Player
    player = CharacterAnimation()
    player.position_x = 100
    player.position_y = 400
    player.set_animation()

    # Lucifer
    from botLevel2 import BotLevel2
    bot = BotLevel2()
    bot.position_x = WIDTH - 220
    bot.position_y = 400
    bot.set_animation()
    bot.is_flipped = True

    # Dialogue font
    font = pygame.font.SysFont("arial", 24, bold=True)

    # Dialogue script: (speaker, message)
    dialogues = [
        ("You", "Lucifer... Your time is over."),
        ("You", "Give back the Orb!!!"),
        ("Lucifer", "Foolish mortal. I will never give it back."),
        ("Lucifer", "The Orb is mine now."),
        ("You", "I will take it back!"),
        ("Lucifer", "You think you can defeat me?"),
        ("You", "I know I cannot... That's why let's play a football match."),
        ("Lucifer", "A football match?"),
        ("You", "Yes, if I win, you give me the Orb."),
        ("Lucifer", "And if I win?"),
        ("You", "Then I will be your servant."),
        ("Lucifer", "Deal."),
        ("You", "Deal."),
        ("Lucifer", "But I will not go easy on you."),
        ("Lucifer", "Prepare to be extinguished."),
    ]

    index = 0
    advance_delay = 600  # ms between advancing dialogue
    waiting = False
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and not waiting:
                index += 1
                waiting = True
                start_time = pygame.time.get_ticks()

        # Allow next key press after delay
        if waiting and pygame.time.get_ticks() - start_time > advance_delay:
            waiting = False

        screen.blit(background, (0, 0))
        player.update(set())
        player.draw(screen)
        bot.update()
        bot.draw(screen)

        if index < len(dialogues):
            speaker, message = dialogues[index]

            # Draw comic-style speech box
            pygame.draw.rect(screen, (255, 255, 255), (80, 50, 640, 100), border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), (80, 50, 640, 100), width=3, border_radius=10)

            # Render text
            speaker_text = font.render(f"{speaker}:", True, (0, 0, 0))
            message_text = font.render(message, True, (0, 0, 0))
            screen.blit(speaker_text, (100, 60))
            screen.blit(message_text, (100, 100))

        else:
            # End of dialogue — fade out and return to Level 2
            pygame.mixer.music.fadeout(1000)
            fade_to_black(screen)
            return

        pygame.display.flip()
        clock.tick(60)





    
# Start menu and story intro
# play_first_video(screen)
# play_intro_scene(screen)
# screen.fill((0, 0, 0))
# pygame.display.flip()
# pygame.time.delay(200)


# # Game level 1
# while True:    
#     if GameLevel1(screen):        
#         break # If player wins level 1, break the loop to transition to level 2
#     else:
#         # If player loses level 1, show restart menu
#         # If player chooses NOT to restart level 1, quit the game
#         pygame.quit()
#         sys.exit()

# # Transition to level 2
# transition_bg = pygame.image.load("images/background/fire_animatiaon.gif")
# transition_bg = pygame.transform.scale(transition_bg, (WIDTH, HEIGHT))

# # play the shake
# screen_shake_effect(screen, transition_bg)

# pygame.mixer.init()
# pygame.mixer.music.load("TransitionLv1Lv2/goingToCastle.mp3")  # replace with your path
# pygame.mixer.music.play()

# castle_zoom_out(screen, "TransitionLv1Lv2/CastleScene.png", duration_ms=12000)
# fade_to_black(screen, duration=1000)
# pygame.mixer.music.stop()

gate_entry_scene(screen, "TransitionLv1Lv2/castle.png")

throne_room_scene(screen)

throne_room_dialogue(screen)


# Game level 2
while True:    
    if GameLevel2(screen):        
        break # If player wins level 2, break the loop to transition to story outro
    else:
        # If player loses level 2, show restart menu
        # If player chooses NOT to restart level 2, quit the game
        pygame.quit()
        sys.exit()  
    

# Story outro


pygame.quit()
sys.exit()