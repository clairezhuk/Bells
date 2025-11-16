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
REACTION_TOLERANCE = 850  # ms (Generous reaction time)
SPAM_THRESHOLD = 2.5 * TIME_UNIT # ms
WIN_COUNT = 24

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (50, 50, 50)
COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0) # Yellow
]
HIGHLIGHT_COLORS = [
    (255, 150, 150),
    (150, 255, 150),
    (150, 150, 255),
    (255, 255, 150)
]

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
    
    # Simple fade out
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

current_cue_key = random.choice(KEYS)
cue_time_start = pygame.time.get_ticks()
hit_this_cue = False

last_press_times = {key: 0 for key in KEYS}

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
                current_cue_key = random.choice(KEYS)
                cue_time_start = current_time
                hit_this_cue = False

        # --- KEY PRESS ---
        if event.type == pygame.KEYDOWN and game_state == "playing":
            if event.key in KEYS:
                key_index = KEY_MAP[event.key]
                
                # 1. Play sound
                SOUNDS[key_index].play()

                # 2. Check for spam
                if current_time - last_press_times[event.key] < SPAM_THRESHOLD:
                    game_state = "lose"
                last_press_times[event.key] = current_time

                # 3. Check for cue hit
                reaction_time = current_time - cue_time_start
                if (not hit_this_cue and 
                    event.key == current_cue_key and 
                    0 < reaction_time < REACTION_TOLERANCE):
                    
                    current_combination.append(event.key)
                    hit_this_cue = True
                
                elif not hit_this_cue:
                    # Wrong key or wrong time
                    current_combination = []
                    hit_this_cue = True # Mark as "failed" for this cue

    # --- Drawing ---
    screen.fill(COLOR_BLACK)

    # Draw cue boxes
    box_size = 150
    padding = 20
    total_width = (box_size + padding) * 4 - padding
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = (SCREEN_HEIGHT - box_size) // 2

    for i in range(4):
        rect = pygame.Rect(start_x + i * (box_size + padding), y_pos, box_size, box_size)
        color = COLOR_GREY
        
        if game_state == "playing" and KEYS[i] == current_cue_key:
            # Highlight the cued key
            time_since_cue = current_time - cue_time_start
            if time_since_cue < REACTION_TOLERANCE:
                color = HIGHLIGHT_COLORS[i]
            else:
                color = COLORS[i] # Show missed cue
        elif game_state != "playing":
             color = COLORS[i]

        pygame.draw.rect(screen, color, rect)
        
        key_text = small_font.render(chr(KEYS[i]).upper(), True, COLOR_BLACK)
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