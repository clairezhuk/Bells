import pygame
import numpy as np
import random
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WIN_COUNT = 24 

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (50, 50, 50)
COLOR_DARK_GREY = (30, 30, 30)

COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0) # Yellow
]
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
# ЗМІНЕНО: Назва вікна
pygame.display.set_caption("Гра Дзвонів") 
clock = pygame.time.Clock()

# Важливо: Pygame не підтримує кирилицю зі шрифтом (None).
# Ми маємо або завантажити шрифт, що її підтримує (напр., 'arial.ttf'),
# або використати вбудований, але тоді текст буде не дуже гарний.
# Спробуємо знайти 'arial' у системі, якщо ні - використаємо None.
try:
    font = pygame.font.SysFont('comicsansms', 60)
    small_font = pygame.font.SysFont('comicsansms', 40)
except:
    print("Шрифт Arial не знайдено, використовую шрифт за замовчуванням.")
    font = pygame.font.Font(None, 74) # Може не відображати кирилицю
    small_font = pygame.font.Font(None, 50)


# Game state variables
game_state = "playing" 
successful_combinations = set()
current_combination = []

# Key state
key_lock_status = {key: 2 for key in KEYS} 

running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- KEY PRESS ---
        if event.type == pygame.KEYDOWN and game_state == "playing":
            if event.key in KEYS:
                pressed_key = event.key
                key_index = KEY_MAP[pressed_key]
                
                # 1. Check for lock
                if key_lock_status[pressed_key] < 2:
                    game_state = "lose_locked"
                    continue 
                
                # 2. Check for internal repeat
                if key_index in current_combination:
                    game_state = "lose_internal_repeat"
                    continue

                # --- Key press is valid, process it ---
                SOUNDS[key_index].play()
                
                key_lock_status[pressed_key] = 0 
                for key in KEYS:
                    if key != pressed_key:
                        key_lock_status[key] += 1

                current_combination.append(key_index)

                if len(current_combination) == 4:
                    combo_tuple = tuple(current_combination)
                    
                    if combo_tuple in successful_combinations:
                        game_state = "lose_repeat"
                    else:
                        successful_combinations.add(combo_tuple)
                        current_combination = []
                        
                        if len(successful_combinations) >= WIN_COUNT:
                            game_state = "win"

    # --- Drawing ---
    screen.fill(COLOR_BLACK)

    # --- Draw Key Boxes (showing lock state) ---
    box_size = 150
    padding = 20
    total_width = (box_size + padding) * 4 - padding
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = (SCREEN_HEIGHT - box_size) // 2

    for i in range(4):
        current_key = KEYS[i]
        rect = pygame.Rect(start_x + i * (box_size + padding), y_pos, box_size, box_size)
        is_locked = key_lock_status[current_key] < 2
        color = HIGHLIGHT_COLORS[i] if is_locked else COLOR_DARK_GREY
        pygame.draw.rect(screen, color, rect)
        
        key_text_color = COLOR_BLACK if is_locked else COLOR_GREY
        # Використовуємо small_font для літер на клавішах (A, S, D, F)
        # Вони залишаються латиницею, тому шрифт 'None' спрацює
        key_text_surface = pygame.font.Font(None, 50).render(chr(current_key).upper(), True, key_text_color)
        text_rect = key_text_surface.get_rect(center=rect.center)
        screen.blit(key_text_surface, text_rect)

    # --- ЗМІНЕНО: Тексти рахунку та комбо ---
    score_text = small_font.render(f"Мелодії: {len(successful_combinations)} / {WIN_COUNT}", True, COLOR_WHITE)
    screen.blit(score_text, (20, 20))

    combo_text = small_font.render(f"Комбо: {len(current_combination)} / 4", True, COLOR_WHITE)
    combo_rect = combo_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
    screen.blit(combo_text, combo_rect)

    # --- ЗМІНЕНО: Блок виведення тексту перемоги/програшу ---
    if game_state == "win":
        win_text = font.render("ПЕРЕМОГА!", True, (0, 255, 0))
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(win_text, text_rect)
        
    elif game_state == "lose_locked":
        # Цей текст може бути задовгим, якщо шрифт 74.
        # Можливо, знадобиться зменшити шрифт у 'font = ...'
        lose_text = font.render("ДЗВІН ЩЕ ЗВУЧИТЬ!", True, (255, 0, 0))
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(lose_text, text_rect)
        
    elif game_state == "lose_repeat":
        lose_text = font.render("МЕЛОДІЯ ПОВТОРИЛАСЬ!", True, (255, 100, 0))
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(lose_text, text_rect)
        
    elif game_state == "lose_internal_repeat":
        lose_text = font.render("ДЗВІН ВЖЕ Є В КОМБО!", True, (255, 100, 100))
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(lose_text, text_rect)
    # --- Кінець зміненого блоку ---

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()