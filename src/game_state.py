import random


class GameState:
    lives = 8
    hint_cost = 20
    correct_letter = 10
    perfect_win = 30

    def __init__(self, word: str):
        if not word:
            raise ValueError()

        self.word = word.upper()
        self.life = self.lives
        self.score = 0
        self.mistakes = 0

        self.guessed = set()
        self.revealed = set()
        self.hint_used = False

        for i, ch in enumerate(self.word):
            if not ch.isalpha():
                self.revealed.add(i)

    @property
    def lives_left(self) -> int:
        return self.life

    def masked(self) -> str:
        result = []
        for i, ch in enumerate(self.word):
            if i in self.revealed:
                result.append(ch)
            else:
                result.append("_")
        return " ".join(result)

    def guess(self, letter: str) -> dict:
        if not letter or len(letter) != 1 or not letter.isalpha():
            return {"error": "invalid input", "lives": self.life, "score": self.score}

        letter = letter.upper()

        if letter in self.guessed:
            return {"already_guessed": True, "lives": self.life, "score": self.score}

        self.guessed.add(letter)

        indices = [i for i, ch in enumerate(self.word) if ch == letter]

        if indices:
            for i in indices:
                self.revealed.add(i)

            gained = len(indices) * self.correct_letter
            self.score += gained

            return {
                "correct": True,
                "points": gained,
                "score": self.score,
                "lives": self.life
            }

        self.life -= 1
        self.mistakes += 1

        return {
            "correct": False,
            "lives": self.life,
            "score": self.score
        }

    def use_hint(self) -> dict:
        if self.is_lost() or self.is_won():
            return {"used": False, "score": self.score}

        if self.score < self.hint_cost:
            return {
                "used": False,
                "reason": "not_enough_score",
                "score": self.score
            }

        hidden_indices = [i for i in range(len(self.word)) if i not in self.revealed]
        if not hidden_indices:
            return {"used": False, "score": self.score}

        index = random.choice(hidden_indices)
        letter = self.word[index]

        for i, ch in enumerate(self.word):
            if ch == letter:
                self.revealed.add(i)

        self.score -= self.hint_cost
        self.hint_used = True

        return {
            "used": True,
            "letter": letter,
            "score": self.score
        }

    def is_won(self) -> bool:
        return all(i in self.revealed for i in range(len(self.word)))

    def is_lost(self) -> bool:
        return self.life <= 0

    def finish_round(self) -> dict:
        bonus = 0
        if self.is_won() and self.mistakes == 0:
            bonus = self.perfect_win

        return {
            "round_score": self.score + bonus,
            "won": self.is_won(),
            "bonus": bonus,
            "mistakes": self.mistakes
        }
