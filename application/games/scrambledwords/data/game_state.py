import logging
import random
from collections import Counter
from threading import Timer
from typing import List, Set, Dict, Optional

from application.games.common.word_manager import WordManager
from application.games.scrambledwords.data.dao import ScrambledWordsDao
from .scoring import Scoring
from .scoring_type import ScoringType
from ..util.time_util import get_time_millis

TOTAL_TILES = 25
TOTAL_TIME_SECONDS = 1 * 60

LOG = logging.getLogger("scrambledwords.GameState")


class GameState:
    """
    Class representing the state of a game.
    """

    def __init__(
        self,
        game_name: str,
        word_manager: WordManager,
        dao: ScrambledWordsDao,
        scoring_type: ScoringType = ScoringType.CLASSIC,
        game_timer: bool = True,
    ):
        """
        Generates a new game state.
        """
        self.game_timer = game_timer
        self.game_name = game_name
        self.word_manager = word_manager
        self.dao = dao
        self.scoring_type = scoring_type

        self.game_tiles: List[str] = []
        self.expire_time: int = None
        self.valid_guesses: Dict[str, Set[str]] = {}
        self.word_counter: Counter = Counter()
        self.game_running = False
        self.end_game_timer: Timer = None

        self.scores: Dict[str, int] = {}
        self.player_ids_to_names: Dict[str, str] = {}

    def new_board(self, tiles: List[str] = None):
        if tiles:
            self.game_tiles = tiles
        else:
            self.game_tiles = GameState._generate_tiles()

        self.word_counter = Counter()
        self.game_running = True

        # Ensure any existing timer is cancelled
        if self.end_game_timer:
            self.end_game_timer.cancel()

        if self.game_timer:
            # Set up the new timer
            self.expire_time = get_time_millis() + (TOTAL_TIME_SECONDS * 1000)
            self.end_game_timer = Timer(TOTAL_TIME_SECONDS, self.end_game)
            self.end_game_timer.start()

        # Dictionary from player ID to Set of valid guesses
        self.valid_guesses = {}

        self._log_info("Created new board")

    def get_board_id(self) -> str:
        board_id = ""
        for tile in self.game_tiles:
            board_id += tile.upper()

        return board_id

    def end_game(self):
        self.game_running = False
        self._log_info("Game ended")

    def get_game_state(self, player_id: str = None) -> Dict[str, object]:
        """
        Returns the state of the game when a player joins or reloads the game.

        Args:
            player_id: the ID of the player joining or reloading the game

        Returns:
            the game state
        """
        game_state = {"expire_time": self.expire_time, "tiles": self.game_tiles}
        if player_id:
            # Set is not serializable so turn it into a set
            game_state["player_guesses"] = list(self.valid_guesses.get(player_id, {}))
            game_state["player_total_score"] = self.scores.get(player_id, 0)
        else:
            # No player_id indicates a reset of the game so send empty guesses list
            game_state["player_guesses"] = []
        return game_state

    def guess_word(self, player_id: str, guessed_word: str) -> Optional[List[int]]:
        """
        Updates the game state to reflect the guessed word.
        If the guess is not correct, the current team's turn is ended.
        Returns the GameUpdate to send to clients.

        Args:
            player_id: The player
            guessed_word: The guessed word

        Returns:
            whether the guess was successful
        """
        # Ensure the guessed word is all lower-case to match with the tiles
        guessed_word = guessed_word.lower()

        # Ensure players are not able to guess after the game has expired
        if not self.game_running:
            self._log_info(f"{player_id} guess word '{guessed_word}' was guessed after game ended")
            return None

        # Ensure players cannot guess the same word multiple times
        if guessed_word in self.valid_guesses.get(player_id, set()):
            self._log_info(f"{player_id} guess word '{guessed_word}' has already been guessed successfully by player")
            return None

        # Check if the word is recognized and on the board
        if self.word_manager.is_word(guessed_word):
            word_is_on_board = self._word_is_on_board(guessed_word)
            if word_is_on_board:
                self._log_info(f"{player_id} guess word '{guessed_word}' is a valid word")

                # Increase the word counter to make it easier to calculate point at the end of the game
                self.word_counter[guessed_word] += 1

                if player_id in self.valid_guesses:
                    self.valid_guesses.get(player_id).add(guessed_word)
                else:
                    valid_guesses = set()
                    valid_guesses.add(guessed_word)
                    self.valid_guesses[player_id] = valid_guesses
            else:
                self._log_info(f"{player_id} guess word '{guessed_word}' is not on the board")

            return word_is_on_board
        else:
            self._log_info(f"{player_id} guess word '{guessed_word}' is not a recognized word")
            return None

    def get_score_state(self, player_id: str, player_name: str) -> Dict[str, object]:
        """
        Called when the player's game timer ends to get the round's score.

        Args:
            player_id: The ID of the player
            player_name: The name of the player

        Returns:
            A dictionary representing the scoring state for the given player for this round
        """
        scored_words = []
        scored_words_values = []
        scored_words_guessers = []
        unscored_words = []
        round_score = 0

        # Total players is the number of players that have at least one valid guess
        total_players = len(self.valid_guesses.keys())

        valid_guesses = self.valid_guesses.get(player_id, set())
        for valid_word in valid_guesses:
            num_player_who_guessed_word = self.word_counter.get(valid_word)
            word_value = Scoring.get_word_value(
                self.scoring_type, valid_word, num_player_who_guessed_word, total_players
            )

            # Record the value of any words with a non-zero value
            if word_value > 0:
                scored_words.append(valid_word)
                scored_words_values.append(word_value)
                round_score += word_value
                scored_words_guessers.append(num_player_who_guessed_word)
            else:
                unscored_words.append(valid_word)

        # Update player's total score
        if player_id in self.scores:
            self.scores[player_id] = self.scores[player_id] + round_score
        else:
            self.scores[player_id] = round_score

        # If there was a score, record it in the database
        if (round_score > 0) and (self.dao is not None):
            self.dao.record_score(self.get_board_id(), round_score, player_name)

        # Send the JSON data back to the player
        return {
            "scored_words": scored_words,
            "scored_word_values": scored_words_values,
            "scored_word_guessers": scored_words_guessers,
            "unscored_words": unscored_words,
            "total_score": self.scores[player_id],
        }

    def _word_is_on_board(self, guessed_word: str) -> Optional[List[int]]:
        possible_paths: List[List[int]] = None

        # Iterate through each character of the guessed word
        for character in guessed_word:
            # Terminate early if we have no possible paths
            if (possible_paths is not None) and (len(possible_paths) == 0):
                break

            # Find all locations where the current character is on the board.
            character_locations = []
            for i in range(0, len(self.game_tiles)):
                if self.game_tiles[i] == character:
                    character_locations.append(i)

            if possible_paths is None:
                # The first character will not have any previous character positions to check.
                possible_paths = [[val] for val in character_locations]
            else:
                # Create a new list for possible paths so that previous paths that will not
                # work with the new character positions are discarded.
                new_possible_paths: List[List[int]] = []

                # Check each character position to see if it can be appended to a possible path.
                for character_location in character_locations:
                    for possible_path in possible_paths:
                        # We cannot use the same tile multiple times in one word.
                        if character_location in possible_path:
                            continue

                        # If the character location is a neighbor of the last tile on a possible
                        # path then we add this as a new possible bath for the next character.
                        if GameState._tiles_are_neighbors(character_location, possible_path[-1]):
                            new_possible_path = possible_path.copy()
                            new_possible_path.append(character_location)
                            new_possible_paths.append(new_possible_path)

                # Swap in the new possible paths to discard paths that are no longer possible.
                possible_paths = new_possible_paths
        LOG.debug(f"Possible paths for '{guessed_word}': {possible_paths}")
        return None if len(possible_paths) == 0 else possible_paths[0]

    def new_player(self, player_id: str, player_name: str):
        self.player_ids_to_names[player_id] = player_name

    def get_players_update(self):
        return {"players": ", ".join(sorted(self.player_ids_to_names.values()))}

    def _log_info(self, log_message: str):
        LOG.info("[%s] %s", self.game_name, log_message)

    @staticmethod
    def _tiles_are_neighbors(tile_index_1: int, tile_index_2: int) -> bool:
        # Calculate the relationship between the two tiles for easier calculation
        smaller_tile = min(tile_index_1, tile_index_2)
        larger_tile = max(tile_index_1, tile_index_2)

        # Ensure we don't go out of bounds
        if (smaller_tile < 0) or (larger_tile >= TOTAL_TILES):
            raise ValueError("Tile indexes invalid")

        difference = larger_tile - smaller_tile

        if larger_tile % 5 == 0:
            # Tiles on the left-most column
            return difference in [4, 5]
        elif (larger_tile + 1) % 5 == 0:
            # Tiles on the right-most column
            return difference in [1, 5, 6]
        else:
            # All other tiles
            return difference in [1, 4, 5, 6]

    @staticmethod
    def _generate_tiles() -> List[str]:
        tiles = []
        for i in range(0, TOTAL_TILES):
            tiles.append(
                random.choice(
                    [
                        "a",
                        "a",
                        "a",
                        "a",
                        "b",
                        "c",
                        "d",
                        "d",
                        "e",
                        "e",
                        "e",
                        "e",
                        "e",
                        "f",
                        "g",
                        "h",
                        "h",
                        "h",
                        "i",
                        "i",
                        "i",
                        "i",
                        "j",
                        "k",
                        "l",
                        "l",
                        "m",
                        "n",
                        "o",
                        "o",
                        "o",
                        "o",
                        "q",
                        "r",
                        "r",
                        "s",
                        "s",
                        "s",
                        "s",
                        "t",
                        "t",
                        "t",
                        "u",
                        "u",
                        "u",
                        "v",
                        "w",
                        "x",
                        "y",
                        "z",
                    ]
                )
            )
        return tiles
