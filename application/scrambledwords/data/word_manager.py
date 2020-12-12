import os
from typing import Set

FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))


class WordManager:
    def __init__(self, words: Set[str] = None):
        if words is None:
            self.words = set()
            with open(f"{FILE_LOCATION}/../../static/scrambledwords/words.txt", mode="r") as word_file:
                for line in word_file:
                    line = line.strip().lower()
                    self.words.add(line)

            print(f"Loaded {len(self.words)} words.")
        else:
            self.words = words

    def is_word(self, word: str) -> bool:
        return word.lower() in self.words
