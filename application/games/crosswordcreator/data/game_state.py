import logging
from typing import Dict, List, Tuple, Set

from .board import Board
from .tiles import Tiles
from ...common.word_manager import WordManager

STARTING_TILES_PER_PLAYER = 20
TILES_PER_PLAYER = STARTING_TILES_PER_PLAYER * 2
BOARD_SIZE = 25
EXCHANGE_TILES = 3

LOG = logging.getLogger("crosswordcreator.GameState")


class GameState:
    """
    Class representing the state of a game.
    """

    def __init__(self, game_name: str, word_manager: WordManager):
        """
        Generates a new game state.
        """
        self.game_name = game_name
        self.word_manager = word_manager

        self.player_ids_to_tiles: Dict[str, List[str]] = {}
        self.player_ids_to_boards: Dict[str, Board] = {}

        self.tiles_left = -1
        self.winning_player_id = None
        self.game_running = False

    def new_player(self, player_id: str, player_name: str) -> bool:
        """
        Method to call when a new player joins the game.
        Players can only join games that are not in progress.

        Args:
            player_id: The ID of the player
            player_name: The display name of the player

        Returns:
            True if the player successfully joined the game, False otherwise.
        """

        if self.game_running:
            self._log_info(f"Player {player_id}/{player_name} attempted to join a game that has already started.")
            return False
        else:
            self._log_info(f"Player {player_id}/{player_name} has joined game.")
            self.player_ids_to_boards[player_id] = Board(player_id, BOARD_SIZE, self.word_manager)
            self.player_ids_to_tiles[player_id] = []
            return True

    def start_game(self):
        # Reset the boards
        for player_id in self.player_ids_to_boards:
            self.player_ids_to_boards[player_id] = Board(player_id, BOARD_SIZE, self.word_manager)

        # Reset the tiles
        self.tiles_left = TILES_PER_PLAYER * len(self.player_ids_to_boards.keys())
        self._generate_player_tiles()

        self.game_running = True
        self._log_info("Game started")

    def end_game(self, winning_player: str):
        """
        Method to call when a game is over.

        Args:
            winning_player: The player that one the game.
        """
        self.game_running = False
        self.winning_player_id = winning_player
        self._log_info(f"Game ended. Winning player: ${winning_player}")

    def get_game_state(self, player_id: str) -> Dict[str, object]:
        """
        Returns the state of the game when a player joins or reloads the game.

        Args:
            player_id: the ID of the player joining or reloading the game

        Returns:
            the game state
        """
        game_state = {
            "num_players": len(self.player_ids_to_boards),
            "tiles_left": self.tiles_left,
            "players": {},
            "game_running": self.game_running,
        }
        player_dict = {"hand_tiles": self.player_ids_to_tiles[player_id]}
        player_dict = {**player_dict, **self.player_ids_to_boards[player_id].get_json()}
        game_state["players"][player_id] = player_dict

        return game_state

    def add_tile(self, player_id: str, hand_tile_index: int, board_position: Tuple[int, int]) -> None:
        """
        Adds the tile with the given index in the player's hand to their board at the given position.

        Args:
            player_id: The ID of the player
            hand_tile_index: The index of the tile in the player's hand
            board_position: The position on the board
        """
        # Remove the tile from the player's hand
        tile = self.player_ids_to_tiles[player_id].pop(hand_tile_index)

        # Add the tile we are replacing if the position on the board already has a tile
        replaced_tile = self.player_ids_to_boards[player_id].add_tile(tile, board_position[0], board_position[1])
        if replaced_tile:
            self.player_ids_to_tiles[player_id].append(replaced_tile)

    def remove_tile(self, player_id: str, board_position: Tuple[int, int]) -> None:
        """
        Method to call when a player removes a tile from their board.
        This method will also update the player's hand.

        Args:
            player_id: The ID of the player
            board_position: The position on the board that the player wants to remove
        """
        removed_tile = self.player_ids_to_boards[player_id].remove_tile(board_position[0], board_position[1])
        if removed_tile:
            self.player_ids_to_tiles[player_id].append(removed_tile)

    def exchange_tile(self, player_id: str, hand_tile_index: int) -> List[str]:
        """
        Method to call when a player exchanges a tile in their hand with three from the pile.
        This method will update the player's hand.

        Args:
            player_id: The player ID
            hand_tile_index: The index of the tile in the player's hand

        Returns:
            The tiles that were added to the player's hand.
        """
        if self.tiles_left < EXCHANGE_TILES:
            raise ValueError("Cannot exchange. Not enough tiles.")

        self.player_ids_to_tiles[player_id].pop(hand_tile_index)
        new_tiles = Tiles.generate_tiles(EXCHANGE_TILES)
        self.player_ids_to_tiles[player_id].extend(new_tiles)
        self.tiles_left -= EXCHANGE_TILES
        return new_tiles

    def peel(self, player_id: str) -> Set[Tuple[int, int]]:
        """
        Method to call when a player attempts to peel.
        If the peel is successful, this method will add a tile to every player's hand.

        Args:
            player_id: The ID of the player

        Returns:
            A set of positions on the board that are not valid. May be empty, indicating a successful peel.
        """
        if not self.game_running:
            raise ValueError("Cannot peel while game is over.")

        invalid_positions = self.player_ids_to_boards[player_id].board_is_valid_crossword()

        if len(invalid_positions) == 0:
            for player_id in self.player_ids_to_tiles.keys():
                self.player_ids_to_tiles[player_id].append(Tiles.generate_tile())
                self.tiles_left -= 1

        # If there are no more tiles to give out, end the game
        if self.tiles_left < 0:
            self.end_game(player_id)

        return invalid_positions

    def _generate_player_tiles(self):
        for player_id in self.player_ids_to_tiles.keys():
            self.player_ids_to_tiles[player_id] = Tiles.generate_tiles(STARTING_TILES_PER_PLAYER)
            self.tiles_left -= STARTING_TILES_PER_PLAYER

    def _log_info(self, log_message: str):
        LOG.info("[%s] %s", self.game_name, log_message)
