import random
from typing import List


class Tiles:
    """
    Class to handle methods around tiles.
    """

    @staticmethod
    def generate_tiles(num_tiles: int) -> List[str]:
        """
        Generates a given number of tiles.
        Tile generation is weighted on English letter frequency.

        Args:
            num_tiles: The number of tiles.

        Returns:
            The tiles.
        """
        return [Tiles.generate_tile() for _ in range(num_tiles)]

    @staticmethod
    def generate_tile() -> str:
        return random.choice(
            [
                "a",
                "a",
                "a",
                "a",
                "b",
                "b",
                "c",
                "d",
                "d",
                "e",
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
