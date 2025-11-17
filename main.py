import pygame
import numpy as np
import random
import sys
import math
import os # Потрібен для шляхів до файлів

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
COLOR_BUTTON = (70, 70, 90)
COLOR_BUTTON_TEXT = (220, 220, 255)

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

# --- Sound Setup (ЗМІНЕНО) ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
# Збільшуємо кількість каналів для одночасного програвання
pygame.mixer.set_num_channels(16) 

# Функція generate_sound() та FREQUENCIES видалені

SOUND_DIR = "sounds"
# Переконуємось, що імена файлів відповідають запиту
sound_filenames = ["зв1.mp3", "зв2.mp3", "зв3.mp3", "зв4.mp3"]
sound_files = [os.path.join(SOUND_DIR, f) for f in sound_filenames]
SOUNDS = []

try:
    SOUNDS = [pygame.mixer.Sound(f) for f in sound_files]
except pygame.error as e:
    print("-" * 50)
    print(f"ПОМИЛКА: Не вдалося завантажити звуки з папки '{SOUND_DIR}'!")
    print(f"Будь ласка, переконайтесь, що папка 'sounds' існує,")
    print(f"і в ній лежать файли: {', '.join(sound_filenames)}")
    print(f"Деталі помилки: {e}")
    print("-" * 50)
    pygame.quit()
    sys.exit()
# --- Кінець Sound Setup ---


# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Гра Дзвонів") 
clock = pygame.time.Clock()

try:
    font = pygame.font.SysFont('comicsansms', 60)
    small_font = pygame.font.SysFont('comicsansms', 40)
except:
    print("Шрифт Comic Sans MS не знайдено, використовую шрифт за замовчуванням.")
    font = pygame.font.Font(None, 74) 
    small_font = pygame.font.Font(None, 50)

# --- НОВА Кнопка "Ще раз" ---
restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50)

# --- НОВА Функція скидання гри ---
# Це запобігає "витоку пам'яті" (старі комбінації залишаються)
def reset_game():
    game_state = "playing"
    successful_combinations = set()
    current_combination = []
    # Скидаємо блокування клавіш
    key_lock_status = {key: 2 for key in KEYS} 
    print("--- Гру перезапущено ---")
    return game_state, successful_combinations, current_combination, key_lock_status

# --- Ініціалізація стану гри (ЗМІНЕНО) ---
game_state, successful_combinations, current_combination, key_lock_status = reset_game()

running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- НОВА Логіка натискання кнопки миші ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Перевіряємо, чи ми в стані програшу і чи натиснули кнопку
            if game_state.startswith("lose") and restart_button_rect.collidepoint(event.pos):
                game_state, successful_combinations, current_combination, key_lock_status = reset_game()

        # --- KEY PRESS ---
        # Кнопки працюють ТІЛЬКИ в стані 'playing'
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
                
                # 3. Play sound (ЗМІНЕНО)
                # .play() автоматично знайде вільний канал
                SOUNDS[key_index].play()
                
                # 4. Update lock states
                key_lock_status[pressed_key] = 0 
                for key in KEYS:
                    if key != pressed_key:
                        key_lock_status[key] += 1

                # 5. Add to current combination
                current_combination.append(key_index)

                # 6. Check if combination is complete
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
        
        key_text_surface = pygame.font.Font(None, 50).render(chr(current_key).upper(), True, (COLOR_BLACK if is_locked else COLOR_GREY))
        text_rect = key_text_surface.get_rect(center=rect.center)
        screen.blit(key_text_surface, text_rect)

    # Draw score
    score_text = small_font.render(f"Мелодії: {len(successful_combinations)} / {WIN_COUNT}", True, COLOR_WHITE)
    screen.blit(score_text, (20, 20))

    # Draw current combo progress
    combo_text = small_font.render(f"Комбо: {len(current_combination)} / 4", True, COLOR_WHITE)
    combo_rect = combo_text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
    screen.blit(combo_text, combo_rect)

    # --- ЗМІНЕНО: Логіка відображення стану гри та кнопки ---
    if game_state == "win":
        win_text = font.render("ПЕРЕМОГА!", True, (0, 255, 0))
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(win_text, text_rect)
        
    elif game_state.startswith("lose"):
        message = ""
        color = (255, 0, 0)
        
        if game_state == "lose_locked":
            message = "ДЗВІН ЩЕ ЗВУЧИТЬ!"
            color = (255, 0, 0)
        elif game_state == "lose_repeat":
            message = "МЕЛОДІЯ ПОВТОРИЛАСЬ!"
            color = (255, 100, 0)
        elif game_state == "lose_internal_repeat":
            message = "ДЗВІН ВЖЕ Є В КОМБО!"
            color = (255, 100, 100)
        
        # Малюємо повідомлення про програш
        lose_text = font.render(message, True, color)
        text_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(lose_text, text_rect)
        
        # НОВЕ: Малюємо кнопку "Ще раз"
        pygame.draw.rect(screen, COLOR_BUTTON, restart_button_rect, border_radius=10)
        button_text = small_font.render("Спробувати ще раз", True, COLOR_BUTTON_TEXT)
        button_text_rect = button_text.get_rect(center=restart_button_rect.center)
        screen.blit(button_text, button_text_rect)
    # --- Кінець зміненого блоку ---

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()