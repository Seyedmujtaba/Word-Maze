# Word-Maze 
A Python + PyQt5 Word Puzzle Game  
Created by: **Seyedmujtaba Tabatabaee & Ayla Rasouli**

---

## 🎯 Overview  
**Guess The Word** is a modern, clean, and visually polished word-guessing puzzle game built with **Python** and **PyQt5**.  
Players select a category, guess letters using an on-screen keyboard, and try to reveal the hidden word before running out of lives.

This project is ideal for learning GUI development in Python while also producing a complete, attractive desktop game.

---

## ✨ Features  

### 🧩 Core Gameplay  
- Category selection (Animals, Fruits, Colors, etc.)  
- Random word generation  
- Word displayed as blank letter slots  
- On-screen A–Z keyboard  
- Correct/incorrect guess detection  
- Win and Game Over conditions  

### 🎮 Game Mechanics  
- +10 points for each correct letter  
- –5 points for incorrect guesses  
- +30 perfect round bonus (no mistakes)  
- Hint system: reveals one random letter  
- Difficulty levels: Easy, Medium, Hard  

### 🖥️ UI / UX  
- Glass-style modern UI inspired by iOS  
- Semi-transparent rounded panels  
- Clean and minimal layout  
- Lives shown as circular indicators  
- Optional animations and effects  

### 💾 Progress Saving  
Stored in JSON:
- Total score  
- Games won / lost  
- Best win streak  
- Highest difficulty cleared  
- Leaderboard  

### 🧱 Technical Structure  
- **GameState** class → handles game logic  
- **MainWindow** class → handles the PyQt UI  
- Modular and scalable architecture  

---

## 📂 Suggested Project Structure

GuessTheWord/
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
│ ├── GDD_English_Designed.pdf
│ ├── GDD_English_Designed_Graphic.pdf
│ └── README_images/
│
└── README.md

yaml
Copy code

---

## 🚀 Installation & Running

### 1️⃣ Install Dependencies  
```bash
pip install PyQt5
2️⃣ Run the Game
bash
Copy code
python main.py
⚙️ Configuration
Editing Word Categories
Located in: data/words.json

Example:

json
Copy code
{
  "Animals": ["dog", "cat", "horse"],
  "Fruits": ["apple", "banana", "orange"],
  "Colors": ["red", "green", "yellow"]
}
Adjusting Game Settings
Lives, UI colors, animations, and difficulty rules can be changed inside:

bash
Copy code
src/game_state.py  
src/main_window.py
🌟 Future Improvements
Planned enhancements:

Sound effects (click, win, wrong guess)

Advanced animations and transitions

Custom themes (Dark Mode, Neon, Material UI)

Time Attack mode

Online leaderboard

Word-definition API

Mobile version (Kivy)

🧪 Developer Notes
UI and logic are intentionally separated for maintainability.

The project structure is modular, allowing easy feature expansion.

Ideal for beginners and intermediate developers learning GUI programming.

📝 Credits
Developed by:

Seyedmujtaba Tabatabaee

Ayla Rasouli

Part of the Word-Maze project initiative.
Documentation and design assisted using AI-powered tools.

📄 License
A software license has not been added yet.
Recommended option: MIT License for open-source distribution.


