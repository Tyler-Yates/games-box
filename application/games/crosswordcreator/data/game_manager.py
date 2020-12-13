import random
import string
from typing import Optional

from .game_state import GameState
from ...common.word_manager import WordManager


class CrosswordCreatorGameManager:
    """
    Manages all the games.
    """

    def __init__(self, word_manager: WordManager):
        self.games = {}
        self.word_manager = word_manager

    def create_game(self) -> GameState:
        """
        Creates a new game.

        Returns:
            the game state
        """
        game_name = self._create_game_name()
        while game_name in self.games:
            game_name = self._create_game_name()

        return self.create_game_for_name(game_name)

    def create_game_for_name(self, game_name: str) -> GameState:
        """
        Creates a new game with the given game name.

        Returns:
            the game state
        """
        game_state = GameState(game_name, self.word_manager)
        self.games[game_name] = game_state

        return game_state

    def get_game_state(self, game_name: str) -> Optional[GameState]:
        """
        Returns the game state for the given game name if one exists.
        Args:
            game_name: the game name

        Returns:
            the game state if one exists
        """
        game_name = game_name.upper()
        return self.games.get(game_name, None)

    @staticmethod
    def _create_game_name() -> str:
        game_name = ""
        for i in range(0, 3):
            game_name += random.choice(string.ascii_uppercase)
        return "CC" + game_name

    def _expire_game(self):
        # TODO we should expire games so that they don't live in memory forever.
        pass
