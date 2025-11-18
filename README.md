# 🔔 The Bells Game (Гра Дзвонів)

A unique pattern and logic game developed to illustrate a mathematical sequencing problem.

## 🇬🇧 English Readme

## The Concept: Permutations and Sequencing

This project simulates a game environment based on a classic mathematical puzzle involving sequencing elements under specific constraint rules.

The core challenge is to successfully input **24 unique 4-key combinations (permutations)** before repeating any combination or breaking the **Bell Constraint**.

### 🧩 The Bell Constraint Logic

The game uses a dynamic locking mechanism:

* **Locking:** After a key (bell) is pressed, it becomes **LOCKED**.
* **Unlocking:** The bell is only **UNLOCKED** and available to be pressed again after **two other unique keys** have been pressed since its last use. This ensures a complex, non-sequential rhythm where all bells are given time to 'ring out'.
* **Game Over (Loss Conditions):**
    1.  Pressing a **LOCKED** bell (`ДЗВІН ЩЕ ЗВУЧИТЬ!`).
    2.  Pressing a key that **already exists** in the current 4-key sequence (`ДЗВІН ВЖЕ Є В КОМБО!`).
    3.  Completing a **4-key sequence** that has already been registered (`МЕЛОДІЯ ПОВТОРИЛАСЬ!`).

## 🚀 How to Play

### Web Version (Recommended)

The web version is the primary way to interact with the game, featuring full mouse/touch support.

1.  **Launch:** Navigate directly to the public GitHub Pages link:
    [https://clairezhuk.github.io/Bells/](https://clairezhuk.github.io/Bells/)

2.  **Controls:** You can control the bells using three methods:
    * **Keyboard:** Press **A, S, D, F**.
    * **Mouse/Touch:** Click or tap the corresponding colored squares.
    * **Mobile Devices:** Tap the buttons directly on the screen.

3.  **Note on Sound:** If the sounds do not load or play on the first attempt, try **refreshing the page several times**. This often resolves browser caching and audio policy issues.

---

### Desktop Version (Windows)

The desktop version is provided as a simple, standalone executable, recommended for users with **slow internet** or difficulties loading audio assets in the browser.

1.  **Launch:** Download the executable file: `dist/bells.exe`.
2.  **Controls:** Input is available **only via the keyboard** (A, S, D, F).

### 🖥️ Development

The core logic for the desktop application is found in `bells.py`.

***

## 🇺🇦 Українське Readme

## Концепція: Перестановки та Послідовності

Цей проєкт симулює ігрове середовище, засноване на ілюстрації математичної задачі про складання послідовностей елементів з урахуванням певних обмежень.

Основне завдання полягає в тому, щоб успішно ввести **24 унікальні комбінації з 4 клавіш (перестановки)**, не повторивши жодної комбінації та не порушивши **Правило Дзвону**.

### 🧩 Логіка обмеження Дзвону

У грі використовується динамічний механізм блокування:

* **Блокування:** Після натискання клавіші (дзвону) вона стає **ЗАБЛОКОВАНОЮ**.
* **Розблокування:** Дзвін **РОЗБЛОКОВУЄТЬСЯ** і стає доступним для повторного натискання лише після того, як були натиснуті **дві інші унікальні клавіші** з моменту його останнього використання. Це забезпечує складний, нелінійний ритм, у якому всі дзвони встигають "дозвучати".
* **Програш (Умови поразки):**
    1.  Натискання **ЗАБЛОКОВАНОГО** дзвону (`ДЗВІН ЩЕ ЗВУЧИТЬ!`).
    2.  Натискання клавіші, яка **вже є** у поточній послідовності з 4 клавіш (`ДЗВІН ВЖЕ Є В КОМБО!`).
    3.  Завершення **послідовності з 4 клавіш**, яка вже була зареєстрована (`МЕЛОДІЯ ПОВТОРИЛАСЬ!`).

## 🚀 Як грати

### Веб-версія (Рекомендовано)

Веб-версія є основним способом взаємодії з грою та має повну підтримку миші/сенсорного введення.

1.  **Запуск:** Перейдіть безпосередньо за публічним посиланням на GitHub Pages:
    [https://clairezhuk.github.io/Bells/](https://clairezhuk.github.io/Bells/)

2.  **Керування:** Керувати дзвонами можна трьома способами:
    * **Клавіатура:** Натискайте **A, S, D, F**.
    * **Миша/Сенсор:** Клацайте або торкайтеся відповідних кольорових квадратів.
    * **Мобільні пристрої:** Натискайте кнопки безпосередньо на екрані.

3.  **Примітка щодо звуку:** Якщо звуки не завантажуються або не відтворюються з першого разу, рекомендується **кілька разів оновити сторінку**. Це часто вирішує проблеми з кешуванням браузера та політикою аудіо.

---

### Десктопна версія (Windows)

Десктопна версія надається як простий автономний виконуваний файл. Вона рекомендована для користувачів із **повільним інтернетом** або проблемами із завантаженням аудіо у браузері.

1.  **Запуск:** Завантажте виконуваний файл: `dist/bells.exe`.
2.  **Керування:** Доступне **лише за допомогою клавіатури** (A, S, D, F).

### 🖥️ Розробка

Код на Python для десктопної версії міститься у файлі `bells.py`.
