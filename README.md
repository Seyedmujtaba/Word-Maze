# Word-Maze 
A Python + PyQt5 Word Puzzle Game  
**Created by:** *Seyedmujtaba Tabatabaee & Ayla Rasouli*

---

## 🎯 Overview  
**Guess The Word** is a clean, modern, and visually polished word-guessing puzzle game built using **Python** and **PyQt5**.  
Players select a category, guess letters from an on-screen keyboard, and try to reveal the hidden word before running out of lives.

This project is ideal for Python beginners and intermediate developers who want to learn GUI programming while building a fully functional game.

---

## ✨ Features  

### 🧩 Core Gameplay  
- Category selection (Animals, Fruits, Colors, etc.)  
- Random word selection  
- Word displayed as blank letter slots  
- On-screen A–Z keyboard  
- Correct / incorrect guess detection  
- Win and Game Over screens  

### 🎮 Game Mechanics  
- +10 points for each correct letter  
- –5 points for incorrect guesses  
- +30 bonus for solving the word with zero mistakes  
- Hint system (reveals one random letter)  
- Difficulty modes: **Easy**, **Medium**, **Hard**  

### 🖥️ UI / UX  
- Glass-style iOS-like design  
- Rounded transparent panels  
- Lives displayed as circular indicators  
- Clean, minimal, readable layout  
- Optional animations and effects  

### 💾 Progress Saving  
Saved in JSON format:
- Total score  
- Wins / Losses  
- Best streak  
- Hardest difficulty completed  
- Leaderboard support  

### 🧱 Technical Structure  
- **GameState** → handles core game logic  
- **MainWindow (PyQt5)** → handles all UI elements  
- Modular, clean, and scalable architecture  

---

## 📂 Suggested Project Structure

Word-Maze/

│

├── assets/

│ ├── icons/

│ └── themes/

│

├── data/

│ ├── words.json

│ └── save_data.json

│

├── src/

│ ├── main.py

│ ├── ui_main.py

│ ├── game_state.py

│ ├── logic_handler.py

│ └── utils.py

│
├── docs/

│ ├── word-maze.pdf

│ └── README_images/

│

└── README.md


---

## 🚀 Installation & Running

### 1️⃣ Install Requirements  
pip install PyQt5


### 2️⃣ Run the Game
python main.py

⚙️ Configuration
Word Categories

Located in: data/words.json

Example:

{
  "Animals": ["dog", "cat", "horse"],
  
  "Fruits": ["apple", "banana", "orange"],
  
  "Colors": ["red", "green", "yellow"]
}

Game Settings

Modify gameplay rules, animations, UI colors, and lives inside:

src/game_state.py
src/main_window.py

📝 Credits

Developed by:

Seyedmujtaba Tabatabaee
Ayla Rasouli

