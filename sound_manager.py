import pygame
import os

# Initialize sounds dictionary
sounds = {}
music_playing = None

def initialize_sounds():
    """Load all game sounds into memory"""
    global sounds
    
    # Create sounds directory if it doesn't exist
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("Created 'sounds' directory. Please add sound files there.")
        return
    
    # Define sound file paths
    sound_files = {
        'background': 'sounds/background_music.mp3',
        'power_shot': 'sounds/power_shot.mp3',
        'vine_power': 'sounds/vine_power.mp3',
        'ball_kick': 'sounds/ball_kick.mp3',
        'ball_ground': 'sounds/ball_ground.mp3',
        'goal_player': 'sounds/goal_player.mp3',
        'goal_enemy': 'sounds/demon_goal.wav',
        'whistle': 'sounds/whistle.mp3',
        'start_button': 'sounds/start_button_press.mp3',
        'menu_sound': 'sounds/game_background.mp3',
        'whistle': 'sounds/whistle.mp3',
        'win': 'sounds/level_win.mp3',
        'retry': 'sounds/retry_page.wav',
        'bomb': 'sounds/bomb.mp3',
        'meteor': 'sounds/nuke.mp3',
        'hurt': 'sounds/ough-47202.mp3',
        'dragon_growl': 'storyscene/dragon-growl-37570.mp3',
    }
    
    # Load each sound into the dictionary
    for name, path in sound_files.items():
        try:
            if os.path.exists(path):
                if name == 'background':
                    # Don't load background music until we need it
                    continue
                else:
                    sounds[name] = pygame.mixer.Sound(path)
                    print(f"Loaded sound: {name}")
            else:
                print(f"Sound file not found: {path}")
        except pygame.error:
            print(f"Could not load sound file: {path}")
    
    # Set default volumes
    for sound_name in sounds:
        sounds[sound_name].set_volume(0.5)  # 50% volume by default

def play_sound(sound_name, loop=False):
    """Play a sound effect"""
    global sounds
    if sound_name in sounds and sounds[sound_name]:
        try:
            # Handle the loop parameter (especially for menu_sound)
            if loop:
                channel = sounds[sound_name].play(-1)  # -1 means loop indefinitely
            else:
                channel = sounds[sound_name].play()
            return channel
        except:
            print(f"Error playing sound: {sound_name}")
    return None

def play_background_music(music_name):
    """Play background music in a loop"""
    global music_playing
    
    # Stop any currently playing music
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    
    # Load and play the new music
    music_path = f'sounds/{music_name}.mp3'
    if os.path.exists(music_path):
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.3)  # 30% volume for background music
            pygame.mixer.music.play(-1)  # Loop indefinitely
            music_playing = music_name
            print(f"Playing background music: {music_name}")
        except pygame.error:
            print(f"Could not load music file: {music_path}")
    else:
        print(f"Music file not found: {music_path}")

def stop_all_sounds():
    """Stop all sound effects"""
    pygame.mixer.stop()

def stop_background_music():
    """Stop the background music"""
    pygame.mixer.music.stop()
    global music_playing
    music_playing = None
    
# Add this to sound_manager.py
def stop_sound(sound_name):
    """Stop a specific sound effect"""
    global sounds
    if sound_name in sounds and sounds[sound_name]:
        try:
            sounds[sound_name].stop()
            print(f"Stopped sound: {sound_name}")
        except:
            print(f"Error stopping sound: {sound_name}")