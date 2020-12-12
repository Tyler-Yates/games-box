from typing import Union

from application.scrambledwords.data.scoring_type import ScoringType


class Scoring:
    @staticmethod
    def get_classic_word_value(word: str) -> int:
        if len(word) <= 4:
            return 1
        elif len(word) == 5:
            return 2
        elif len(word) == 6:
            return 3
        elif len(word) == 7:
            return 5
        elif len(word) == 8:
            return 8
        elif len(word) > 8:
            return 11
        return 0

    @staticmethod
    def get_word_value(
        scoring_type: ScoringType, word: str, num_player_who_guessed_word: int, total_players: int
    ) -> Union[int, float]:
        if scoring_type == ScoringType.CLASSIC:
            # If multiple players guessed the word, it is worth nothing
            if num_player_who_guessed_word > 1:
                return 0
            return Scoring.get_classic_word_value(word)
        else:
            # Words that everyone guessed should not count for points
            if num_player_who_guessed_word == total_players:
                return 0

            # Distributed scoring takes into account the number of players who guessed a word
            distributed_value: float = Scoring.get_classic_word_value(word) / num_player_who_guessed_word

            if scoring_type == ScoringType.DISTRIBUTED_FRACTIONAL:
                # Return a float rounded to two decimal places
                return round(distributed_value, 2)
            else:
                # Integer division always rounds down
                return int(distributed_value)
