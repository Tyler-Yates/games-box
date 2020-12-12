import logging
import random
from typing import List, Dict

from .game_tile import GameTile
from .game_update import GameUpdate
from application.games.common.word_manager import WordManager

WORD_COUNT = 25
BLUE_TEAM_TILES = 9
RED_TEAM_TILES = 8

LOG = logging.getLogger("GameState")


class GameState:
    """
    Class representing the state of a game.
    """

    def __init__(self, game_name: str, word_manager: WordManager):
        """
        Generates a new, random game state.
        """
        self.game_name = game_name
        self.game_tiles: Dict[str, GameTile] = dict()

        self.blue_team_tiles_remaining = BLUE_TEAM_TILES
        self.red_team_tiles_remaining = RED_TEAM_TILES
        self.current_team = 1
        self.winning_team = None

        words = self._generate_words(word_manager)
        hidden_values = self._generate_hidden_values()
        for i in range(0, WORD_COUNT):
            word = words[i]
            hidden_value = hidden_values[i]
            self.game_tiles[word] = GameTile(word, hidden_value)

        self._log_info("Created new game")

    def end_turn(self) -> GameUpdate:
        """
        Ends the current team's turn and creates the GameUpdate to send to clients.

        Returns:
            the game update
        """
        self._log_info(f"Team {self.current_team} turn is over")

        if self.current_team == 1:
            self.current_team = 2
        else:
            self.current_team = 1

        return GameUpdate(self, [])

    def guess_word(self, guessed_word: str) -> GameUpdate:
        """
        Updates the game state to reflect the guessed word.
        If the guess is not correct, the current team's turn is ended.
        Returns the GameUpdate to send to clients.

        Args:
            guessed_word: The guessed word

        Returns:
            the game update
        """
        self._log_info(f"Team {self.current_team} has guessed word {guessed_word}")

        game_tile = self.game_tiles.get(guessed_word, None)

        # Ensure the guess is actually valid
        if (game_tile is None) or game_tile.guessed:
            raise ValueError(f"Invalid guess: '{guessed_word}'")

        # Ensure guesses cannot come in after a win
        if self.winning_team:
            raise ValueError("A team has already won.")

        # Mark the tile as guessed
        game_tile.guessed = True

        # Incorrect guesses should end the current team's turn
        if game_tile.hidden_value != self.current_team:
            self.end_turn()

        # Adjust team tile values accordingly
        if game_tile.hidden_value == 1:
            self.blue_team_tiles_remaining -= 1
        elif game_tile.hidden_value == 2:
            self.red_team_tiles_remaining -= 1
        elif game_tile.hidden_value == 3:
            # Assassin is always an incorrect guess so the current team has already been changed
            self.winning_team = self.current_team

        # See if any team has won
        if self.blue_team_tiles_remaining == 0:
            self.winning_team = 0
        elif self.red_team_tiles_remaining == 0:
            self.winning_team = 1

        # Return a GameUpdate object so clients can update the page
        return GameUpdate(self, [game_tile.to_json()])

    def get_tiles_json(self) -> List[Dict[str, str]]:
        """
        Returns the current tiles in a list of JSON compatible dictionaries.

        Returns:
            the tiles
        """
        tiles = list()
        for tile in self.game_tiles.values():
            tiles.append(tile.to_json())
        return tiles

    def get_game_update(self) -> GameUpdate:
        """
        Returns the entire board state to send to clients as a GameUpdate.

        Returns:
            the game update
        """
        return GameUpdate(self)

    def _log_info(self, log_message: str):
        LOG.info("[%s] %s", self.game_name, log_message)

    @staticmethod
    def _generate_words(word_manager: WordManager) -> List[str]:
        return word_manager.get_random_words(WORD_COUNT)

    @staticmethod
    def _generate_hidden_values() -> List[int]:
        possible_values = list(range(0, WORD_COUNT))
        hidden_values = [0] * WORD_COUNT

        # Assassin
        index = random.randint(0, len(possible_values) - 1)
        assassin_location = possible_values[index]
        possible_values.pop(index)
        hidden_values[assassin_location] = 3

        # Blue team
        for i in range(0, BLUE_TEAM_TILES):
            index = random.randint(0, len(possible_values) - 1)
            location = possible_values[index]
            possible_values.pop(index)
            hidden_values[location] = 1

        # Red team
        for i in range(0, RED_TEAM_TILES):
            index = random.randint(0, len(possible_values) - 1)
            location = possible_values[index]
            possible_values.pop(index)
            hidden_values[location] = 2

        return hidden_values
