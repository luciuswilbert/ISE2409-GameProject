import pygame
import time
import sys
import cv2
import numpy as np
from botLevel2 import BotLevel2  # Lucifer animation class

pygame.mixer.init()


def play_intro_scene(screen):
    # Load background images
    bg_with_orb = pygame.image.load("images/background/scene01.png")
    bg_with_orb = pygame.transform.scale(bg_with_orb, (800, 600))

    bg_without_orb = pygame.image.load("images/background/scene02.jpeg")
    bg_without_orb = pygame.transform.scale(bg_without_orb, (800, 600))

    grass_sound = pygame.mixer.Sound("storyscene/grasssound.mp3")
    grass_sound.set_volume(0.3)  # optional, reduce volume

    # Load all run frames for exit animation
    lucifer_run_frames = [
        pygame.transform.scale(
            pygame.image.load(f"images/bot_level_2/Run A-{str(i).zfill(2)}.png"), (150, 200)
        )
        for i in range(1, 9)
    ]
    lucifer_run_frame_index = 0
    lucifer_run_frame_counter = 0
    lucifer_exit_frame_delay = 5

    # BotLevel2 Lucifer animation (enter, idle)
    lucifer = BotLevel2()
    lucifer.position_x = 900
    lucifer.position_y = 400
    lucifer.current_action = "run"
    lucifer.set_animation()
    lucifer.is_flipped = True

    # Separate manual tracking for exiting phase
    lucifer_exit_x = 430
    lucifer_exit_y = 400

    clock = pygame.time.Clock()
    running = True
    phase = "start"
    phase_start_time = time.time()
    lucifer_moving = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

        current_time = time.time()

        # PHASE LOGIC
        if phase == "start":
            if current_time - phase_start_time >= 5:
                phase = "entering"

        elif phase == "entering":
            lucifer.position_x -= 2
            if lucifer.position_x <= 430:
                lucifer.position_x = 430
                lucifer.current_action = "idle"
                lucifer.set_animation()
                phase = "waiting"
                phase_start_time = current_time

        elif phase == "waiting":
            if current_time - phase_start_time > 1.5:
                phase = "orb_gone"
                phase_start_time = current_time

        elif phase == "orb_gone":
            if current_time - phase_start_time > 0.5:
                lucifer.current_action = "run"
                lucifer.set_animation()
                lucifer.is_flipped = False
                lucifer_exit_x = lucifer.position_x
                phase = "exiting"

        elif phase == "exiting":
            lucifer_exit_x += 2
            if not pygame.mixer.get_busy():
                grass_sound.play()
            lucifer_run_frame_counter += 1
            
            if lucifer_run_frame_counter >= lucifer_exit_frame_delay:
                lucifer_run_frame_counter = 0
                lucifer_run_frame_index = (lucifer_run_frame_index + 1) % len(lucifer_run_frames)

            if lucifer_exit_x > 1000:
                pygame.time.delay(3000)  # Wait 3 seconds
                play_second_video(screen)
                running = False



        # DRAW BACKGROUND
        if phase in ["orb_gone", "exiting"]:
            screen.blit(bg_without_orb, (0, 0))
        else:
            screen.blit(bg_with_orb, (0, 0))

        # DRAW CHARACTER
        if phase == "exiting":
            current_frame = lucifer_run_frames[lucifer_run_frame_index]
            screen.blit(current_frame, (lucifer_exit_x, lucifer_exit_y - 50))
        elif phase != "start":
            lucifer.update()
            lucifer.draw(screen)

        # Determine if Lucifer is currently moving
        if phase in ["entering", "exiting"]:
            lucifer_moving = True
        else:
            lucifer_moving = False

        # Play or stop grass sound accordingly
        if lucifer_moving:
            if not pygame.mixer.get_busy():
                grass_sound.play()  # -1 = loop indefinitely
        else:
            grass_sound.stop()


        pygame.display.flip()
        clock.tick(60)

# def play_chaos_video(screen):
#     cap = cv2.VideoCapture("storyscene/chaosNoOrb.mp4")

#     if not cap.isOpened():
#         print(" Could not open video.")
#         return

#     clock = pygame.time.Clock()

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Convert BGR (OpenCV) to RGB (Pygame)
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame = np.rot90(frame)  # Rotate if needed
#         surface = pygame.surfarray.make_surface(frame)
#         surface = pygame.transform.scale(surface, screen.get_size())

#         screen.blit(surface, (0, 0))
#         pygame.display.flip()
#         clock.tick(30)  # Match your video FPS

#     cap.release()

def play_first_video(screen):
    cap = cv2.VideoCapture("storyscene/firstVideo.mp4")
    if not cap.isOpened():
        print("❌ Could not open video.")
        return

    clock = pygame.time.Clock()

    pygame.mixer.music.load("storyscene/firstVideo.mp3")

    start_time = pygame.time.get_ticks()  # Record start time
    music_played = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        surface = pygame.surfarray.make_surface(frame)
        surface = pygame.transform.scale(surface, screen.get_size())
        surface = pygame.transform.flip(surface, True, False) 


        screen.blit(surface, (0, 0))
        pygame.display.flip()

        if not music_played and pygame.time.get_ticks() - start_time >= 2000:
            pygame.mixer.music.play()
            music_played = True

        clock.tick(30)

    cap.release()
    pygame.mixer.music.stop()

def play_second_video(screen):
    cap = cv2.VideoCapture("storyscene/revisionChaos.mp4")
    if not cap.isOpened():
        print("Could not open video.")
        return

    clock = pygame.time.Clock()

    pygame.mixer.music.load("storyscene/revisionChaos.mp3")

    start_time = pygame.time.get_ticks()  # Record start time
    music_played = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        surface = pygame.surfarray.make_surface(frame)
        surface = pygame.transform.scale(surface, screen.get_size())
        surface = pygame.transform.flip(surface, True, False) 

        screen.blit(surface, (0, 0))
        pygame.display.flip()

        if not music_played and pygame.time.get_ticks() - start_time >= 1000:
            pygame.mixer.music.play()
            music_played = True

        clock.tick(30)

    cap.release()
    pygame.mixer.music.stop()










