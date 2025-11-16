import pygame
import numpy as np
import random
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

TIME_UNIT = 1000  # ms (1 second)
REACTION_TOLERANCE = 850  # ms (Reaction window after cue)
SPAM_THRESHOLD = 2.5 * TIME_UNIT # ms
WIN_COUNT = 24

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (50, 50, 50)
COLOR_DARK_GREY = (30, 30, 30)
COLOR_CUE_ON = (200, 200, 255) # Light blue for cue
COLOR_CUE_OFF = (40, 40, 60)

COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0) # Yellow
]
# These colors are now used for the SPAM cooldown
HIGHLIGHT_COLORS = COLORS 

# Keys
KEYS = [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f]
KEY_MAP = {KEYS[i]: i for i in range(len(KEYS))}

# Sound generation
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

def generate_sound(frequency, duration=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = np.zeros((n_samples, 2), dtype=np.int16)
    amplitude = 2**15 - 1
    t = np.linspace(0., duration, n_samples, endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    
    fade_len = int(sample_rate * 0.01)
    if n_samples > fade_len:
        fade_out = np.linspace(1, 0, fade_len)
        wave[n_samples-fade_len:] *= fade_out

    buf[:, 0] = wave.astype(np.int16)
    buf[:, 1] = wave.astype(np.int16)
    return pygame.sndarray.make_sound(buf)

# Notes (C4, D4, E4, F4)
FREQUENCIES = [261.63, 293.66, 329.63, 349.23]
SOUNDS = [generate_sound(freq) for freq in FREQUENCIES]

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Rhythm Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 50)

# Game state variables
game_state = "playing" # "playing", "win", "lose"
successful_combinations = set()
current_combination = []

# Cue state
cue_time_start = pygame.time.get_ticks()
hit_this_cue = False # Has the user hit a key for the current cue?

# Key state
last_press_times = {key: -SPAM_THRESHOLD for key in KEYS} # Init timers to be ready

# Timers
NEXT_CUE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(NEXT_CUE_EVENT, TIME_UNIT)

running = True
while running:
    current_time = pygame.time.get_ticks()

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- CUE TIMER ---
        if event.type == NEXT_CUE_EVENT and game_state == "playing":
            if not hit_this_cue:
                # User missed the cue
                current_combination = []

            if len(current_combination) >= 4:
                successful_combinations.add(tuple(current_combination))
                current_combination = []
                
                if len(successful_combinations) >= WIN_COUNT:
                    game_state = "win"

            if game_state == "playing":
                # Start the next cue
                cue_time_start = current_time
                hit_this_cue = False

        # --- KEY PRESS ---
        if event.type == pygame.KEYDOWN and game_state == "playing":
            if event.key in KEYS:
                key_index = KEY_MAP[event.key]
                
                # 1. Check for spam
                if current_time - last_press_times[event.key] < SPAM_THRESHOLD:
                    game_state = "lose"
                    continue # Stop processing this key press

                # 2. Play sound
                SOUNDS[key_index].play()
                
                # 3. Update press time *after* spam check
                last_press_times[event.key] = current_time

                # 4. Check for cue hit
                reaction_time = current_time - cue_time_start
                if (not hit_this_cue and 
                    0 < reaction_time < REACTION_TOLERANCE):
                    
                    # Successful hit
                    current_combination.append(key_index) # Store index
                    hit_this_cue = True
                
                elif not hit_this_cue:
                    # Hit at the wrong time (too early/late)
                    current_combination = []
                    hit_this_cue = True # Mark as "failed" for this cue

    # --- Drawing ---
    screen.fill(COLOR_BLACK)

    # --- Draw CUE Indicator (Metronome) ---
    is_cue_active = (current_time - cue_time_start < REACTION_TOLERANCE) and game_state == "playing"
    cue_color = COLOR_CUE_ON if is_cue_active and not hit_this_cue else COLOR_CUE_OFF
    cue_rect = pygame.Rect((SCREEN_WIDTH - 100) // 2, 50, 100, 50)
    pygame.draw.rect(screen, cue_color, cue_rect, border_radius=10)


    # --- Draw Key Boxes (showing cooldown) ---
    box_size = 150
    padding = 20
    total_width = (box_size + padding) * 4 - padding
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = (SCREEN_HEIGHT - box_size) // 2

    for i in range(4):
        rect = pygame.Rect(start_x + i * (box_size + padding), y_pos, box_size, box_size)
        
        # Check if the key is on spam cooldown
        time_since_last_press = current_time - last_press_times[KEYS[i]]
        is_on_cooldown = time_since_last_press < SPAM_THRESHOLD
        
        # Key lights up if on cooldown
        color = HIGHLIGHT_COLORS[i] if is_on_cooldown else COLOR_DARK_GREY

        pygame.draw.rect(screen, color, rect)
        
        key_text_color = COLOR_BLACK if is_on_cooldown else COLOR_GREY
        key_text = small_font.render(chr(KEYS[i]).upper(), True, key_text_color)
        text_rect = key_text.get_rect(center=rect.center)
        screen.blit(key_text, text_rect)

    # Draw score
    score_text = small_font.render(f"Score: {len(successful_combinations)} / {WIN_COUNT}", True, COLOR_WHITE)
    screen.blit(score_text, (20, 20))

    # Draw game state
    if game_state == "win":
        win_text = font.render("YOU WIN!", True, (0, 255, 0))
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(win_text, text_rect)
    elif game_state == "lose":
        lose_text = font.render("GAME OVER (SPAM)", True, (255, 0, 0))
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        screen.blit(lose_text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()