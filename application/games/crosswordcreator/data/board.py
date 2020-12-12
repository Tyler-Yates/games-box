from typing import List, Optional, Tuple, Set, Dict

from ...common.word_manager import WordManager


class Board:
    """
    Represents a board for a single player.
    Boards are assumed to be square (equal number of rows and columns).

    The board is represented as a two dimensional matrix.
    Points on the board are represented as tuples of integers: (row, column).
    The upper-left corner of the board is point (0,0).
    The lower-right corner of the board is point (board_size-1, board_size-1).
    """

    def __init__(self, player_id: str, board_size: int, word_manager: WordManager):
        self.player_id = player_id
        self.board_size = board_size
        self.board: List[List[Optional[str]]] = [[None for _ in range(board_size)] for _ in range(board_size)]
        self.word_manager = word_manager

    def _set_board(self, board: List[List[Optional[str]]]):
        # Helper method for tests to set the board how they like.
        self.board_size = len(board)
        self.board = board

    def add_tile(self, tile: str, row: int, col: int) -> Optional[str]:
        """
        Adds a tile to the given position on the board.

        Args:
            tile: The tile
            row: The row
            col: The column

        Returns:
            The tile that was previously at that location. Could be None.
        """
        previous_tile = self.board[row][col]
        self.board[row][col] = tile
        return previous_tile

    def remove_tile(self, row: int, col: int) -> Optional[str]:
        """
        Removes the tile from the given position on the board.

        Args:
            row: The row
            col: The column

        Returns:
            The tile that was removed. Could be None.
        """
        removed_tile = self.board[row][col]
        self.board[row][col] = None
        return removed_tile

    def _find_connected_tiles(self, row, col, non_empty_tiles_not_visited: set) -> None:
        """
        Recursive function used to find all connected tiles from a given point.
        NOTE: non_empty_tiles_not_visited will be modified by this function.

        Args:
            row: The starting row
            col: The starting column
            non_empty_tiles_not_visited: The complete set of non-empty tiles for this function to work with
        """

        non_empty_tiles_not_visited.remove((row, col))

        if (row > 0) and (self.board[row - 1][col] is not None) and ((row - 1, col) in non_empty_tiles_not_visited):
            self._find_connected_tiles(row - 1, col, non_empty_tiles_not_visited)
        if (
            (row < self.board_size - 1)
            and (self.board[row + 1][col] is not None)
            and ((row + 1, col) in non_empty_tiles_not_visited)
        ):
            self._find_connected_tiles(row + 1, col, non_empty_tiles_not_visited)
        if (col > 0) and (self.board[row][col - 1] is not None) and ((row, col - 1) in non_empty_tiles_not_visited):
            self._find_connected_tiles(row, col - 1, non_empty_tiles_not_visited)
        if (
            (col < self.board_size - 1)
            and (self.board[row][col + 1] is not None)
            and ((row, col + 1) in non_empty_tiles_not_visited)
        ):
            self._find_connected_tiles(row, col + 1, non_empty_tiles_not_visited)

    def _check_connected(self) -> Set[Tuple[int, int]]:
        """
        Function used to check if all tiles on the board are connected.

        Returns:
            A set of points on the board that are not connected. May be empty which indicates all tiles are connected.
        """
        first_tile = None
        non_empty_tiles = set()

        # Find the first tile and all tiles that are non-empty
        for row in range(self.board_size):
            for col in range(self.board_size):
                tile = self.board[row][col]
                if tile is not None:
                    non_empty_tiles.add((row, col))
                    if first_tile is None:
                        first_tile = (row, col)

        # Traverse through all tiles reachable from the first tile.
        # Whatever tiles are left in non_empty_tiles are not connected.
        self._find_connected_tiles(first_tile[0], first_tile[1], non_empty_tiles)
        return non_empty_tiles

    def _check_valid_words(self) -> Set[Tuple[int, int]]:
        """
        Helper method to check that all words in the crossword of the board are valid.

        Returns:
            A set of points that are part of invalid words.
            This may be empty, indicating the board is a valid crossword.
        """
        invalid_points = set()
        # Check across each row
        for row in range(self.board_size):
            current_word = ""
            for col in range(self.board_size):
                tile = self.board[row][col]
                # If the position is blank, it's time to check
                if tile is None:
                    # If we have a current word of length more than 1, check its validity
                    if len(current_word) > 1:
                        # If the word is not valid, add the points to the list of invalid points
                        if not self.word_manager.is_word(current_word):
                            for i in range(len(current_word)):
                                invalid_points.add((row, col - 1 - i))
                    # Now that we are done with our checks, we clear the current word to continue our search
                    current_word = ""
                else:
                    current_word += tile

            # The current word could go to the end of the board so we need to do an additional check
            if not self.word_manager.is_word(current_word):
                for i in range(len(current_word)):
                    invalid_points.add((row, self.board_size - 1 - i))

        # Check down each column
        for col in range(self.board_size):
            current_word = ""
            for row in range(self.board_size):
                tile = self.board[row][col]
                # If the position is blank, it's time to check
                if tile is None:
                    # If we have a current word of length more than 1, check its validity
                    if len(current_word) > 1:
                        # If the word is not valid, add the points to the list of invalid points
                        if not self.word_manager.is_word(current_word):
                            for i in range(len(current_word)):
                                invalid_points.add((row - 1 - i, col))
                    # Now that we are done with our checks, we clear the current word to continue our search
                    current_word = ""
                else:
                    current_word += tile

            # The current word could go to the end of the board so we need to do an additional check
            if not self.word_manager.is_word(current_word):
                for i in range(len(current_word)):
                    invalid_points.add((self.board_size - 1 - i, col))

        return invalid_points

    def board_is_valid_crossword(self) -> Set[Tuple[int, int]]:
        """
        Returns whether the board represents a valid crossword.

        Returns:
            A set of invalid points on the board. If empty, the board is a valid crossword.
        """
        # First check is to ensure that all tiles on the board are connected.
        unconnected_points = self._check_connected()
        if unconnected_points:
            return unconnected_points

        # Now, ensure all tiles make a valid crossword of recognized words.
        return self._check_valid_words()

    def shift_board_down(self) -> bool:
        """
        Shifts the entire board down one row if possible.

        Returns:
            True if the shift occurred, False otherwise
        """
        for c in range(self.board_size):
            if self.board[self.board_size - 1][c] is not None:
                return False

        for r in range(self.board_size - 1, 0, -1):
            for c in range(self.board_size):
                self.board[r][c] = self.board[r - 1][c]

        for c in range(self.board_size):
            self.board[0][c] = None

        return True

    def shift_board_up(self) -> bool:
        """
        Shifts the entire board up one row if possible.

        Returns:
            True if the shift occurred, False otherwise
        """
        for c in range(self.board_size):
            if self.board[0][c] is not None:
                return False

        for r in range(0, self.board_size - 1):
            for c in range(self.board_size):
                self.board[r][c] = self.board[r + 1][c]

        for c in range(self.board_size):
            self.board[self.board_size - 1][c] = None

        return True

    def shift_board_right(self) -> bool:
        """
        Shifts the entire board right one row if possible.

        Returns:
            True if the shift occurred, False otherwise
        """
        for r in range(self.board_size):
            if self.board[r][self.board_size - 1] is not None:
                return False

        for c in range(self.board_size - 1, 0, -1):
            for r in range(self.board_size):
                self.board[r][c] = self.board[r][c - 1]

        for r in range(self.board_size):
            self.board[r][0] = None

        return True

    def shift_board_left(self) -> bool:
        """
        Shifts the entire board left one row if possible.

        Returns:
            True if the shift occurred, False otherwise
        """
        for r in range(self.board_size):
            if self.board[r][0] is not None:
                return False

        for c in range(0, self.board_size - 1):
            for r in range(self.board_size):
                self.board[r][c] = self.board[r][c + 1]

        for r in range(self.board_size):
            self.board[r][self.board_size - 1] = None

        return True

    def get_json(self) -> Dict[str, object]:
        return {"board": self.board}
