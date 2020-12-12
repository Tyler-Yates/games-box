from application.games.common.word_manager import WordManager

TEST_WORD_SET = {"test", "DOG", "Cat"}


class TestWordManager:
    def setup_method(self):
        self.word_manager = WordManager(words=TEST_WORD_SET)

    def test_valid_words(self):
        assert self.word_manager.is_word("test") is True
        assert self.word_manager.is_word("TEST") is True
        assert self.word_manager.is_word("dog") is True
        assert self.word_manager.is_word("DOG") is True
        assert self.word_manager.is_word("cat") is True
        assert self.word_manager.is_word("CAT") is True

    def test_invalid_words(self):
        assert self.word_manager.is_word("123") is False
        assert self.word_manager.is_word("abc") is False
        assert self.word_manager.is_word("cats") is False

    def test_num_words(self):
        assert self.word_manager.num_words() == len(TEST_WORD_SET)

    def test_get_random_words(self):
        num_words = 1
        random_words = self.word_manager.get_random_words(num_words)
        assert len(random_words) == num_words
        for random_word in random_words:
            assert self.word_manager.is_word(random_word)

        num_words = 3
        random_words = self.word_manager.get_random_words(num_words)
        assert len(random_words) == num_words
        for random_word in random_words:
            assert self.word_manager.is_word(random_word)
