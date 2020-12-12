import logging
import os
import random
from typing import List, Set

LOG = logging.getLogger("word_manager")

FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))


class WordManager:
    def __init__(self, words: Set[str] = None, word_file_path: str = ""):
        # If we are given a set of words, use those and return early
        if words is not None:
            self.words = words
            return

        # Otherwise, load the given file of words
        self.words = set()
        with open(f"{FILE_LOCATION}/../../static/{word_file_path}", mode="r") as word_file:
            for line in word_file:
                line = line.strip().upper()
                self.words.add(line)

        LOG.debug(f"Loaded {len(self.words)} words.")

    def is_word(self, word: str) -> bool:
        return word.lower() in self.words

    def get_random_words(self, number_of_words: int) -> List[str]:
        return random.sample(self.words, number_of_words)

    def num_words(self) -> int:
        return len(self.words)
