from application.games.common.word_manager import WordManager
from application.games.crosswordcreator.data.board import Board


class TestBoard:
    def test_valid_board_1(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]

        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        invalid_points = board.board_is_valid_crossword()
        assert set() == invalid_points

    def test_valid_board_2(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["d", None, None, None, None],
            ["y", None, None, None, None],
        ]

        board = Board("test", 5, WordManager({"daddy", "dad", "bad", "as"}))
        board._set_board(tiles)

        invalid_points = board.board_is_valid_crossword()
        assert set() == invalid_points

    def test_invalid_board_invalid_word(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "z", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]

        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        invalid_points = board.board_is_valid_crossword()
        # Invalid because the two instances of "az" are not valid words
        assert {(0, 3), (1, 2), (1, 3)} == invalid_points

    def test_invalid_board_not_connected(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, "d", "a", "dad"],
        ]

        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        invalid_points = board.board_is_valid_crossword()
        # Invalid because not all tiles are connected
        assert {(4, 2), (4, 3), (4, 4)} == invalid_points

    def test_shift_down_valid(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]
        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert board.shift_board_down()

        expected_tiles = [
            [None, None, None, None, None],
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
        ]

        assert expected_tiles == board.board

    def test_shift_down_invalid(self):
        tiles = [
            [None, None, None, None, None],
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
        ]

        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert not board.shift_board_down()

        # Tiles should not have moved
        assert tiles == board.board

    def test_shift_up_valid(self):
        tiles = [
            [None, None, None, None, None],
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
        ]
        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert board.shift_board_up()

        expected_tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]

        assert expected_tiles == board.board

    def test_shift_up_invalid(self):
        tiles = [
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            [None, None, None, None, None],
        ]
        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert not board.shift_board_up()

        # Tiles should not have moved
        assert tiles == board.board

    def test_shift_right_valid(self):
        tiles = [
            ["d", None, "b", "a", None],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            ["x", None, None, None, None],
        ]
        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert board.shift_board_right()

        expected_tiles = [
            [None, "d", None, "b", "a"],
            [None, "a", None, "a", "s"],
            [None, "d", "a", "d", None],
            [None, "s", None, None, None],
            [None, "x", None, None, None],
        ]

        assert expected_tiles == board.board

    def test_shift_right_invalid(self):
        tiles = [
            [None, None, None, None, None],
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
        ]

        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert not board.shift_board_right()

        # Tiles should not have moved
        assert tiles == board.board

    def test_shift_left_valid(self):
        tiles = [
            [None, "d", None, "b", "a"],
            [None, "a", None, "a", "s"],
            [None, "d", "a", "d", None],
            [None, "s", None, None, None],
            [None, "x", None, None, None],
        ]
        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert board.shift_board_left()

        expected_tiles = [
            ["d", None, "b", "a", None],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
            ["x", None, None, None, None],
        ]

        assert expected_tiles == board.board

    def test_shift_left_invalid(self):
        tiles = [
            [None, None, None, None, None],
            ["d", None, "b", "a", "d"],
            ["a", None, "a", "s", None],
            ["d", "a", "d", None, None],
            ["s", None, None, None, None],
        ]

        board = Board("test", 5, WordManager({"dads", "dad", "bad", "as"}))
        board._set_board(tiles)

        assert not board.shift_board_left()

        # Tiles should not have moved
        assert tiles == board.board
