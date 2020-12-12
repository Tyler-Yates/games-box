from application.games.scrambledwords.data.word_manager import WordManager


class TestWordManager(WordManager):
    def __init__(self):
        super(TestWordManager, self).__init__(set())

    def is_word(self, word: str) -> bool:
        return True
