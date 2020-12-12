from application.games.common.word_manager import WordManager


class AcceptingWordManager(WordManager):
    def __init__(self):
        super(AcceptingWordManager, self).__init__(set())

    def is_word(self, word: str) -> bool:
        return True
