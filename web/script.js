// --- Constants ---
const WIN_COUNT = 24;
const KEY_MAP = {
    'a': { id: 'key-a', soundId: 'sound-a' },
    's': { id: 'key-s', soundId: 'sound-s' },
    'd': { id: 'key-d', soundId: 'sound-d' },
    'f': { id: 'key-f', soundId: 'sound-f' }
};
const KEYS = ['a', 's', 'd', 'f'];
const GAME_MESSAGES = {
    'win': { text: "ПЕРЕМОГА!", color: "#00FF00" },
    'lose_locked': { text: "ДЗВІН ЩЕ ЗВУЧИТЬ!", color: "#FF0000" },
    'lose_repeat': { text: "МЕЛОДІЯ ПОВТОРИЛАСЬ!", color: "#FF6400" },
    'lose_internal_repeat': { text: "ДЗВІН ВЖЕ Є В КОМБО!", color: "#FF6464" }
};

// --- DOM Elements ---
const scoreDisplay = document.getElementById('score-display');
const comboDisplay = document.getElementById('combo-display');
const messageDisplay = document.getElementById('message-display');
const restartButton = document.getElementById('restart-button');
const keyBoxes = {
    'a': document.getElementById('key-a'),
    's': document.getElementById('key-s'),
    'd': document.getElementById('key-d'),
    'f': document.getElementById('key-f')
};
const sounds = {
    'a': document.getElementById('sound-a'),
    's': document.getElementById('sound-s'),
    'd': document.getElementById('sound-d'),
    'f': document.getElementById('sound-f')
};

// --- Нові DOM елементи для модального вікна ---
const modalOverlay = document.getElementById('modal-overlay');
const permissionBox = document.getElementById('permission-box');
const loadingBox = document.getElementById('loading-box');
const btnSoundYes = document.getElementById('btn-sound-yes');
const btnSoundNo = document.getElementById('btn-sound-no');

// --- Game State Variables ---
let gameState = "loading"; // Гра починається в стані "завантаження"
let successfulCombinations;
let currentCombination;
let keyLockStatus;
let useSound = false; // Звук вимкнено за замовчуванням

// --- Game Functions ---

/**
 * Скидає гру до початкового стану.
 * Тепер це лише логіка, UI оновлюється окремо.
 */
function reset_game() {
    console.log("--- Гру перезапущено ---");
    gameState = "playing";
    successfulCombinations = new Set();
    currentCombination = [];
    keyLockStatus = { 'a': 2, 's': 2, 'd': 2, 'f': 2 };
    
    // Оновлюємо UI
    updateUI();
    // Переконуємось, що повідомлення про програш чисті
    messageDisplay.textContent = "";
    restartButton.classList.add('hidden');
}

/**
 * Оновлює весь UI на основі поточного стану гри.
 */
function updateUI() {
    // 1. Оновити рахунок та комбо
    scoreDisplay.textContent = `Мелодії: ${successfulCombinations.size} / ${WIN_COUNT}`;
    comboDisplay.textContent = `Комбо: ${currentCombination.length} / 4`;

    // 2. Оновити вигляд клавіш
    for (const key of KEYS) {
        const isLocked = keyLockStatus[key] < 2;
        const keyElement = keyBoxes[key];
        
        if (isLocked) {
            keyElement.classList.add('locked');
        } else {
            keyElement.classList.remove('locked');
        }
    }
    
    // 3. Оновити повідомлення та кнопку "Ще раз"
    if (gameState === "playing") {
        messageDisplay.textContent = "";
        restartButton.classList.add('hidden');
    } else {
        const message = GAME_MESSAGES[gameState];
        if (message) {
            messageDisplay.textContent = message.text;
            messageDisplay.style.color = message.color;
        }
        
        if (gameState.startsWith("lose")) {
            restartButton.classList.remove('hidden');
        }
    }
}

/**
 * Програє звук. Тепер з перевіркою useSound.
 */
function playSound(key) {
    // ЯКЩО ЗВУК ВИМКНЕНО - НЕ РОБИМО НІЧОГО.
    if (!useSound) {
        return; 
    }
    
    try {
        const sound = sounds[key];
        if (sound) {
            sound.currentTime = 0; 
            const playPromise = sound.play();
            
            if (playPromise !== undefined) {
                playPromise.catch(error => {
                    console.warn(`Асинхронна помилка відтворення ${key} (проігноровано):`, error);
                });
            }
        }
    } catch (error) {
        console.error(`Синхронна помилка при спробі відтворення ${key} (проігноровано):`, error);
    }
}

/**
 * НОВА ФУНКЦІЯ: Примусове завантаження всіх звуків.
 */
function preloadSounds() {
    console.log("Початок завантаження звуків...");
    permissionBox.classList.add('hidden');
    loadingBox.classList.remove('hidden');
    
    const soundPromises = KEYS.map(key => {
        return new Promise((resolve, reject) => {
            const audio = sounds[key];
            
            // Якщо звук вже готовий (з кешу)
            if (audio.readyState >= 4) { // HAVE_ENOUGH_DATA
                resolve(key);
                return;
            }
            
            // Додаємо слухачів
            audio.addEventListener('canplaythrough', () => resolve(key), { once: true });
            audio.addEventListener('error', () => reject(key), { once: true });
            
            // Примусово запускаємо завантаження
            audio.load();
        });
    });
    
    Promise.all(soundPromises)
        .then(() => {
            // ВСЕ ДОБРЕ
            console.log("Всі звуки успішно завантажено!");
            modalOverlay.classList.add('hidden'); // Ховаємо модальне вікно
            reset_game(); // Запускаємо гру
        })
        .catch((failedKey) => {
            // ПОМИЛКА ЗАВАНТАЖЕННЯ
            console.error(`Не вдалося завантажити ${failedKey}. Запуск без звуку.`);
            alert(`Помилка завантаження звуку ${failedKey}. Гра запуститься без звуку.`);
            useSound = false; // Вимикаємо звук
            modalOverlay.classList.add('hidden');
            reset_game();
        });
}

/**
 * Обробник натискання клавіш.
 */
function handleKeyPress(event) {
    const key = event.key.toLowerCase();
    
    if (!KEYS.includes(key)) {
        return;
    }
    
    // Гра працює тільки в стані 'playing'
    if (gameState !== 'playing') {
        return;
    }
    
    // --- Помилки тут бути не може ---
    
    // 1. Перевірка блокування (Key Locked)
    if (keyLockStatus[key] < 2) {
        gameState = "lose_locked";
        playSound(key); // Граємо звук програшу
        updateUI();
        return;
    }
    
    // 2. Перевірка повтору всередині комбо (Internal Repeat)
    if (currentCombination.includes(key)) {
        gameState = "lose_internal_repeat";
        playSound(key);
        updateUI();
        return;
    }

    // --- Натискання валідне ---
    // (Код звідси 100% виконається, бо playSound() тепер безпечний)

    // 3. Граємо звук
    playSound(key);

    // 4. Оновлюємо статус блокування
    keyLockStatus[key] = 0; // Блокуємо натиснуту
    for (const otherKey of KEYS) {
        if (otherKey !== key) {
            keyLockStatus[otherKey] += 1; // Просуваємо інші
        }
    }

    // 5. Додаємо до комбінації
    currentCombination.push(key);

    // 6. Перевірка завершення комбо
    if (currentCombination.length === 4) {
        const comboString = currentCombination.join('');
        
        if (successfulCombinations.has(comboString)) {
            gameState = "lose_repeat";
        } else {
            successfulCombinations.add(comboString);
            currentCombination = [];
            
            if (successfulCombinations.size >= WIN_COUNT) {
                gameState = "win";
            }
        }
    }
    
    // Оновлюємо UI після кожної дії
    updateUI();
}

// --- Event Listeners (ПОВНІСТЮ ЗМІНЕНО) ---

// НЕ запускаємо гру одразу, а чекаємо на рішення користувача
document.addEventListener('DOMContentLoaded', () => {
    // Показати модальне вікно (воно не приховане за замовчуванням)
    gameState = "loading";
});

// Слухач для кнопки "ТАК"
btnSoundYes.addEventListener('click', () => {
    useSound = true;
    preloadSounds(); // Починаємо завантаження
});

// Слухач для кнопки "НІ"
btnSoundNo.addEventListener('click', () => {
    useSound = false;
    modalOverlay.classList.add('hidden'); // Ховаємо вікно
    reset_game(); // Негайно починаємо гру
});

// Слухаємо натискання клавіш
document.addEventListener('keydown', handleKeyPress);

// Слухаємо натискання кнопки "Ще раз"
restartButton.addEventListener('click', reset_game);