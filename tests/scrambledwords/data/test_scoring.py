from application.scrambledwords.data.scoring import Scoring
from application.scrambledwords.data.scoring_type import ScoringType


class TestScoring:
    def test_get_word_value_classic(self):
        for word_length in range(3, 10):
            word = "a" * word_length
            assert Scoring.get_classic_word_value(word) == Scoring.get_word_value(ScoringType.CLASSIC, word, 1, 4)
            assert 0 == Scoring.get_word_value(ScoringType.CLASSIC, word, 2, 4)
            assert 0 == Scoring.get_word_value(ScoringType.CLASSIC, word, 3, 4)

    def test_get_word_value_distributed_fractional_3_letters(self):
        assert 1 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "aaa", 1, 4)
        assert 0.5 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "aaa", 2, 4)
        assert 0.33 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "aaa", 3, 4)
        assert 0 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "aaa", 4, 4)

    def test_get_word_value_distributed_integer_3_letters(self):
        assert 1 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "aaa", 1, 4)
        assert 0 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "aaa", 2, 4)
        assert 0 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "aaa", 3, 4)
        assert 0 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "aaa", 4, 4)

    def test_get_word_value_distributed_fractional_7_letters(self):
        assert 5 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "a" * 7, 1, 4)
        assert 2.5 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "a" * 7, 2, 4)
        assert 1.67 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "a" * 7, 3, 4)
        assert 0 == Scoring.get_word_value(ScoringType.DISTRIBUTED_FRACTIONAL, "a" * 7, 4, 4)

    def test_get_word_value_distributed_integer_7_letters(self):
        assert 5 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "a" * 7, 1, 4)
        assert 2 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "a" * 7, 2, 4)
        assert 1 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "a" * 7, 3, 4)
        assert 0 == Scoring.get_word_value(ScoringType.DISTRIBUTED_INTEGER, "a" * 7, 4, 4)
