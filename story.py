import pygame
import sys
import random

from config import *
from storyscene.introscene1 import *
from character import *
from botLevel2 import BotLevel2 
from sound_manager import play_sound, play_background_music


def screen_shake_effect(screen, background_img, duration_ms=5000, intensity=10):
    clock = pygame.time.Clock()
    start = pygame.time.get_ticks()
    fade_start = duration_ms - 1000  # start fade 1s before end
    pygame.mixer.music.load("TransitionLv1Lv2/rumble.mp3") 
    pygame.mixer.music.play()

    screen_width, screen_height = screen.get_size()

    running = True
    while running:
        now = pygame.time.get_ticks()
        elapsed = now - start

        # Quit or ESC
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

        if elapsed >= duration_ms:
            break

        dx = random.randint(-intensity, intensity)
        dy = random.randint(-intensity, intensity)
        screen.fill((0, 0, 0))
        screen.blit(background_img, (dx, dy))

        # Fading overlay
        if elapsed >= fade_start:
            fade_alpha = int(255 * (elapsed - fade_start) / 1000)  # 0 → 255 over 1 sec
            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.set_alpha(fade_alpha)
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    # Final fade to black
    fade_surface = pygame.Surface((screen_width, screen_height))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
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

    screen_width, screen_height = screen.get_size()

    running = True
    while running:
        now = pygame.time.get_ticks()
        elapsed = now - start_time

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

        if elapsed > duration_ms:
            break

        # Linear interpolation of scale
        t = elapsed / duration_ms
        current_scale = start_scale * (1 - t) + end_scale * t

        scaled_w = int(base_width * current_scale)
        scaled_h = int(base_height * current_scale)
        scaled_img = pygame.transform.smoothscale(original_img, (scaled_w, scaled_h))

        x = (screen_width - scaled_w) // 2
        y = (screen_height - scaled_h) // 2

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
    player.set_animation()  

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
    pygame.mixer.music.play(-1)

    background = pygame.image.load("images/background/throne room.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    player = CharacterAnimation()
    player.position_x = 100
    player.position_y = 400
    player.set_animation()

    bot = BotLevel2()
    bot.position_x = WIDTH - 220
    bot.position_y = 400
    bot.stationary = True
    bot.set_animation()
    bot.is_flipped = True 

    start_time = pygame.time.get_ticks()
    duration = 3000

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if pygame.time.get_ticks() - start_time > duration:
            pygame.mixer.music.fadeout(1000)  
            running = False

        screen.blit(background, (0, 0))
        player.update(set()) 
        player.draw(screen)

        bot.update()
        bot.draw(screen)

        pygame.display.flip()
        clock.tick(60)

def throne_room_dialogue(screen):
    clock = pygame.time.Clock()

    pygame.mixer.music.load("storyscene/beforeLuciferSoundTrack.mp3")
    pygame.mixer.music.play(-1)  

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
    bot.stationary = True
    bot.is_flipped = True

    # Dialogue font
    font = pygame.font.SysFont("arial", 24, bold=True)

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
            # End of dialogue — fade out and return to Level 2d
            pygame.mixer.music.fadeout(1000)
            fade_to_black(screen)
            return

        pygame.display.flip()
        clock.tick(60)

def throne_room_dialogue_after(screen):
    clock = pygame.time.Clock()

    pygame.mixer.music.load("storyscene/beforeLuciferSoundTrack.mp3")
    pygame.mixer.music.play(-1)  

    background = pygame.image.load("images/background/throne room.png").convert()
    background = pygame.transform.scale(background, screen.get_size())

    # Player
    player = CharacterAnimation()
    player.position_x = 100
    player.position_y = 400
    player.set_animation()

    # Lucifer
    bot = BotLevel2()
    bot.position_x = screen.get_width() - 220
    bot.position_y = 400
    bot.current_action = "idle"
    bot.set_animation()
    bot.is_flipped = True

    # Dialogue font
    font = pygame.font.SysFont("arial", 24, bold=True)

    # Dialogue script: (speaker, message)
    dialogues = [
        ("You", "YES!!!, I won!"),
        ("You", "Now give me the Orb."),
        ("Lucifer", "You think I will give it to you?"),
        ("Lucifer", "I will never give it to you."),
        ("You", "But we made a deal."),
        ("Lucifer", "A deal?"),
        ("Lucifer", "I don't remember any deal."),
        ("You", "What?"),
        ("Lucifer", "I will keep the Orb and you will be my servant."),
        ("You", "No!!!"),
        ("Lucifer", "HAHAHAHAHAHA"),
    ]

    index = 0
    advance_delay = 600  # ms between advancing dialogue
    waiting = False
    start_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and not waiting:
                index += 1
                waiting = True
                start_time = pygame.time.get_ticks()

        if waiting and pygame.time.get_ticks() - start_time > advance_delay:
            waiting = False

        screen.blit(background, (0, 0))
        player.update(set())
        player.draw(screen)
        bot.stationary = True
        bot.update()
        bot.draw(screen)

        if index < len(dialogues):
            speaker, message = dialogues[index]

            pygame.draw.rect(screen, (255, 255, 255), (80, 50, 640, 100), border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), (80, 50, 640, 100), width=3, border_radius=10)

            speaker_text = font.render(f"{speaker}:", True, (0, 0, 0))
            message_text = font.render(message, True, (0, 0, 0))
            screen.blit(speaker_text, (100, 60))
            screen.blit(message_text, (100, 100))

        else:
            pygame.mixer.music.fadeout(1000)
            fade_to_black(screen)
            move_player_to_lucifer(screen, player, bot, background)
            return

        pygame.display.flip()
        clock.tick(60)


def move_player_to_lucifer(screen, player, bot, background):
    clock = pygame.time.Clock()
    target_x = bot.position_x - 100
    
    if player.current_action != "run":
        player.current_action = "run"
        player.set_animation()

    while player.position_x < target_x:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        player.position_x += player.move_speed
        player.is_flipped = False

        player.update(set())
        bot.update()

        screen.blit(background, (0, 0))
        player.draw(screen)
        bot.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    if player.current_action != "idle":
        player.current_action = "idle"
        player.set_animation()

    player.update(set())
    screen.blit(background, (0, 0))
    player.draw(screen)
    bot.draw(screen)
    pygame.display.flip()
    pygame.time.wait(3000)

    player.current_action = "kick"
    player.set_animation()

    for i in range(len(player.kick_animation)):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        player.update(set())
        screen.blit(background, (0, 0))
        player.draw(screen)
        bot.draw(screen)
        pygame.display.flip()
        pygame.time.delay(100)

    bot.stationary = False
    bot.current_action = "dead"
    bot.set_animation()
    play_sound("hurt", loop=False)

    for i in range(len(bot.dead_animation)):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        bot.frame_index = i
        screen.blit(background, (0, 0))
        player.draw(screen)
        bot.draw(screen)
        pygame.display.flip()
        pygame.time.delay(80)

    screen.blit(background, (0, 0))
    player.draw(screen)
    bot.draw(screen)
    pygame.display.flip()
    pygame.time.wait(3000)

    fade_to_black(screen)
    orb_statue_scene(screen)


def orb_statue_scene(screen):
    clock = pygame.time.Clock()

    # Add background music
    pygame.mixer.music.load("storyscene/graveyardSound.mp3") 
    pygame.mixer.music.play(-1)  

    # Load both backgrounds
    orb_present = pygame.image.load("storyscene/orbAtLucifer.png").convert()
    orb_present = pygame.transform.scale(orb_present, (WIDTH, HEIGHT))

    orb_missing = pygame.image.load("storyscene/orbAtLuciferMissing.jpeg").convert()
    orb_missing = pygame.transform.scale(orb_missing, (WIDTH, HEIGHT))

    # Setup player
    player = CharacterAnimation()
    player.position_x = 100
    player.position_y = 400
    player.set_animation()

    # Define area near statue
    statue_trigger = pygame.Rect(WIDTH - 180, 100, 80, 150)
    # pygame.draw.rect(orb_present, (255, 0, 0), statue_trigger, 2)  # Draw trigger area for debugging
    orb_collected = False

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        # Movement
        moving = False
        jumping = False
        if keys[pygame.K_a]:  # Move left
            player.position_x -= player.move_speed
            player.is_flipped = True
            moving = True
        if keys[pygame.K_d]:  # Move right
            player.position_x += player.move_speed
            player.is_flipped = False
            moving = True
        if keys[pygame.K_SPACE]: # Jump
            jumping = True

        if moving and player.current_action != "run":
            player.current_action = "run"
            player.set_animation()
        elif jumping and player.current_action != "jump":
            player.current_action = "jump"
            player.set_animation()
        elif not moving and player.current_action != "idle":
            player.current_action = "idle"
            player.set_animation()

        player.position_x = max(30, min(WIDTH - 100, player.position_x))
        player.update(keys)

        # Check trigger area
        player_rect = player.rect
        if player_rect.colliderect(statue_trigger):
            orb_collected = True

        # Draw scene
        screen.blit(orb_missing if orb_collected else orb_present, (0, 0))
        player.draw(screen)
        pygame.display.flip()
        clock.tick(60)

        if orb_collected:
            pygame.time.wait(1000)
            pygame.mixer.music.fadeout(1000)
            fade_to_black(screen)
            chaos_statue_scene(screen)
            return

def chaos_statue_scene(screen):
    clock = pygame.time.Clock()

    # Add background music
    pygame.mixer.music.load("storyscene/loudThunder.mp3") 
    pygame.mixer.music.play(-1) 

    # Load both backgrounds
    chaos_bg = pygame.image.load("storyscene/stormBackToFirstBackground.png").convert()
    chaos_bg = pygame.transform.scale(chaos_bg, (WIDTH, HEIGHT))

    orb_restored_bg = pygame.image.load("images/background/scene01.png").convert()
    orb_restored_bg = pygame.transform.scale(orb_restored_bg, (WIDTH, HEIGHT))
    dragon_bg = pygame.image.load("storyscene/dragon.jpg").convert()
    orb_restored_bg = pygame.transform.scale(orb_restored_bg, (WIDTH, HEIGHT))

    # Setup player on the right (carrying orb)
    player = CharacterAnimation()
    player.position_x = WIDTH - 120
    player.position_y = 400
    player.is_flipped = True
    player.set_animation()

    statue_trigger = pygame.Rect((WIDTH // 2) - 30, 180, 100, 120)
    # pygame.draw.rect(chaos_bg, (255, 0, 0), statue_trigger, 2)  # Draw trigger area for debugging
    orb_placed = False

    running = True
    while running:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                pygame.quit()
                sys.exit()

        # Movement
        moving = False
        jumping = False
        if keys[pygame.K_a]:
            player.position_x -= player.move_speed
            player.is_flipped = True
            moving = True
        if keys[pygame.K_d]:
            player.position_x += player.move_speed
            player.is_flipped = False
            moving = True
        if keys[pygame.K_SPACE]:  # Jump
            jumping = True

        if moving and player.current_action != "run":
            player.current_action = "run"
            player.set_animation()
        elif jumping and player.current_action != "jump":
            player.current_action = "jump"
            player.set_animation()
        elif not moving and player.current_action != "idle":
            player.current_action = "idle"
            player.set_animation()

        player.position_x = max(30, min(WIDTH - 100, player.position_x))
        player.update(keys)

        # Check if orb placed
        player_rect = player.rect
        if player_rect.colliderect(statue_trigger):
            orb_placed = True
            pygame.mixer.music.fadeout(1000)


        # Draw scene
        if orb_placed:
            fade_to_black(screen, duration=1200)
            screen.blit(orb_restored_bg, (0, 0))  # change background
            pygame.mixer.music.load("storyscene/birdsChirping.mp3") 
            pygame.mixer.music.play(-1) 
            pygame.mixer.music.load("storyscene/Ending1.mp3")
            pygame.mixer.music.play(0)
            
            # Keep showing background while voice plays
            screen.blit(orb_restored_bg, (0, 0))
            pygame.display.flip()
            pygame.time.wait(25000)  # Wait for voice to finish
            
            play_sound("dragon_growl", loop=False)
            fade_to_black(screen, duration=1500)

            # # Show final scene with animated flying dragon
            end_time = pygame.time.get_ticks() + 5000  # 5 seconds duration
            while pygame.time.get_ticks() < end_time:
                screen.blit(dragon_bg, (0, 0))
                pygame.display.flip()
                clock.tick(60)
            
            fade_to_black(screen, duration=1500)
            return

        screen.blit(chaos_bg, (0, 0))
        player.draw(screen)
        pygame.display.flip()
        clock.tick(60)