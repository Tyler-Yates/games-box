from typing import List, Dict

from application.scrambledwords.data import GameTile


class GameUpdate:
    def __init__(self, game_state: "GameState", tiles: List[GameTile] = None):  # noqa: F821
        self.blue_team_tiles_remaining = game_state.blue_team_tiles_remaining
        self.red_team_tiles_remaining = game_state.red_team_tiles_remaining
        self.current_team = game_state.current_team

        if game_state.winning_team:
            self.winning_team = game_state.winning_team

        if tiles is None:
            self.tiles = game_state.get_tiles_json()
        else:
            self.tiles = tiles

    def to_json(self) -> Dict[str, object]:
        return self.__dict__
