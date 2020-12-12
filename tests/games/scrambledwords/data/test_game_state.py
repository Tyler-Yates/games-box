from typing import List

from application.games.common.word_manager import WordManager
from application.games.scrambledwords.data.game_state import GameState
from ...common.accepting_word_manager import AcceptingWordManager


class TestGameState:
    def setup_method(self):
        # Create a word manager that accepts any word
        word_manager = AcceptingWordManager()

        tiles = [
            "s", "a", "b", "e", "r",
            "j", "t", "t", "s", "x",
            "z", "z", "z", "z", "z",
            "s", "z", "z", "z", "z",
            "z", "z", "z", "z", "z"
        ]

        # Do not set a game timer as pytest cannot handle that
        self.game_state = GameState("test", word_manager, tiles, game_timer=False)

    def test_guess_word_valid(self):
        assert self.game_state.guess_word("player", "set") is not None
        assert self.game_state.guess_word("player", "states") is not None

    def test_guess_word_invalid(self):
        assert self.game_state.guess_word("player", "armory") is None
        assert self.game_state.guess_word("player", "test") is None

    def test_guess_word_unrecognized(self):
        self.game_state.word_manager = WordManager({"test"})
        assert self.game_state.guess_word("player", "word") is None

    def test_word_is_on_board_valid(self):
        assert self.game_state._word_is_on_board("set") is not None
        assert self.game_state._word_is_on_board("sat") is not None
        assert self.game_state._word_is_on_board("state") is not None
        assert self.game_state._word_is_on_board("states") is not None
        assert self.game_state._word_is_on_board("rest") is not None
        assert self.game_state._word_is_on_board("saber") is not None
        assert self.game_state._word_is_on_board("stab") is not None
        assert self.game_state._word_is_on_board("best") is not None
        assert self.game_state._word_is_on_board("bat") is not None
        assert self.game_state._word_is_on_board("bats") is not None

    def test_word_is_on_board_invalid(self):
        assert self.game_state._word_is_on_board("armory") is None

    def test_word_is_on_board_invalid_reuse(self):
        assert self.game_state._word_is_on_board("test") is None
        assert self.game_state._word_is_on_board("jaba") is None

    def test_tiles_are_neighbors_0(self):
        TestGameState._assert_neighbors(0, [1, 5, 6])

    def test_tiles_are_neighbors_1(self):
        TestGameState._assert_neighbors(1, [0, 2, 5, 6, 7])

    def test_tiles_are_neighbors_4(self):
        TestGameState._assert_neighbors(4, [3, 8, 9])

    def test_tiles_are_neighbors_7(self):
        TestGameState._assert_neighbors(7, [1, 2, 3, 6, 8, 11, 12, 13])

    def test_tiles_are_neighbors_20(self):
        TestGameState._assert_neighbors(20, [15, 16, 21])

    def test_tiles_are_neighbors_23(self):
        TestGameState._assert_neighbors(23, [17, 18, 19, 22, 24])

    def test_tiles_are_neighbors_24(self):
        TestGameState._assert_neighbors(24, [18, 19, 23])

    @staticmethod
    def _assert_neighbors(starting_tile: int, neighbors: List[int]):
        for i in range(0, 25):
            if i == starting_tile:
                continue

            if i in neighbors:
                assert GameState._tiles_are_neighbors(starting_tile, i) is True
            else:
                assert GameState._tiles_are_neighbors(starting_tile, i) is False
