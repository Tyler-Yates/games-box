import logging
import os
import random
from typing import List, Set

LOG = logging.getLogger("common.word_manager")

FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))


class WordManager:
    def __init__(self, words: Set[str] = None, word_file_path: str = ""):
        if words is not None:
            # If we are given a set of words, use those
            words = list(set([word.upper() for word in words]))
        else:
            # Otherwise, load the given file of words
            words = set()
            with open(f"{FILE_LOCATION}/../../static/{word_file_path}", mode="r") as word_file:
                for line in word_file:
                    line = line.strip().upper()
                    words.add(line)

        # Sampling from a set is deprecated so turn the set into a list
        self.words = list(words)

        LOG.debug(f"Loaded {len(self.words)} words.")

    def is_word(self, word: str) -> bool:
        return word.upper() in self.words

    def get_random_words(self, number_of_words: int) -> List[str]:
        return random.sample(self.words, number_of_words)

    def num_words(self) -> int:
        return len(self.words)
