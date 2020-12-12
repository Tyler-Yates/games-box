from application.games.crosswordcreator.data.tiles import Tiles


class TestTiles:
    def test_generate_tiles(self):
        num_tiles = 20
        tiles = Tiles.generate_tiles(num_tiles)
        print(f"Tiles: {tiles}")

        assert len(tiles) == num_tiles
