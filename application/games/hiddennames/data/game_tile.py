class GameTile:
    def __init__(self, word: str, hidden_value: int, guessed=False):
        self.word = word
        self.hidden_value = hidden_value
        self.guessed = guessed

    def __repr__(self):
        return f"{self.word} - {self.hidden_value} - {self.guessed}"

    def __str__(self):
        return f"{self.word} - {self.hidden_value} - {self.guessed}"

    def to_json(self):
        return self.__dict__
