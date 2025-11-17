// --- Constants ---
const WIN_COUNT = 24;

// Карта відповідності клавіш (e.key) до їх ID елементів
const KEY_MAP = {
    'a': { id: 'key-a', soundId: 'sound-a' },
    's': { id: 'key-s', soundId: 'sound-s' },
    'd': { id: 'key-d', soundId: 'sound-d' },
    'f': { id: 'key-f', soundId: 'sound-f' }
};
const KEYS = ['a', 's', 'd', 'f'];

// Карта повідомлень про стан гри
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

// --- Game State Variables ---
let gameState;
let successfulCombinations;
let currentCombination;
let keyLockStatus;

// --- Game Functions ---

/**
 * Скидає гру до початкового стану.
 */
function reset_game() {
    console.log("--- Гру перезапущено ---");
    gameState = "playing";
    successfulCombinations = new Set();
    currentCombination = [];
    keyLockStatus = { 'a': 2, 's': 2, 'd': 2, 'f': 2 };
    
    // Оновлюємо UI
    updateUI();
}

/**
 * Оновлює весь UI на основі поточного стану гри.
 */
function updateUI() {
    // 1. Оновити рахунок та комбо
    scoreDisplay.textContent = `Мелодії: ${successfulCombinations.size} / ${WIN_COUNT}`;
    comboDisplay.textContent = `Комбо: ${currentCombination.length} / 4`;

    // 2. Оновити вигляд клавіш (заблоковано/розблоковано)
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
        
        // Показати кнопку "Ще раз" при будь-якому програші
        if (gameState.startsWith("lose")) {
            restartButton.classList.remove('hidden');
        }
    }
}

/**
 * Програє звук. Дозволяє накладання.
 */
function playSound(key) {
    const sound = sounds[key];
    if (sound) {
        sound.currentTime = 0; // Дозволяє повторне швидке натискання
        sound.play();
    }
}

/**
 * Обробник натискання клавіш.
 */
function handleKeyPress(event) {
    const key = event.key.toLowerCase();
    
    // Перевіряємо, чи це одна з наших ігрових клавіш
    if (!KEYS.includes(key)) {
        return;
    }
    
    // Гра працює тільки в стані 'playing'
    if (gameState !== 'playing') {
        return;
    }
    
    // 1. Перевірка блокування (Key Locked)
    if (keyLockStatus[key] < 2) {
        gameState = "lose_locked";
        playSound(key); // Все одно граємо звук, але фіксуємо програш
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
        
        // Перевірка на повний повтор комбо
        if (successfulCombinations.has(comboString)) {
            gameState = "lose_repeat";
        } else {
            // Успіх!
            successfulCombinations.add(comboString);
            currentCombination = [];
            
            // Перевірка на перемогу
            if (successfulCombinations.size >= WIN_COUNT) {
                gameState = "win";
            }
        }
    }
    
    // Оновлюємо UI після кожної дії
    updateUI();
}

// --- Event Listeners ---

// Запускаємо гру, коли сторінка завантажилась
document.addEventListener('DOMContentLoaded', reset_game);

// Слухаємо натискання клавіш
document.addEventListener('keydown', handleKeyPress);

// Слухаємо натискання кнопки "Ще раз"
restartButton.addEventListener('click', reset_game);