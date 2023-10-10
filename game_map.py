import numpy as np
from tcod.console import Console

import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        # Tiles the player can currently see
        self.visible = np.full((width, height), fill_value=False, order="F")
        # Tiles the player has seen before
        self.explored = np.full((width, height), fill_value=False, order="F")

    
    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x & y are within bounds of map"""
        return 0 <= x < self.width and 0 <= y < self.height
    

    def render(self, console: Console) -> None:
        """
        Renders the map

        If a tile is in the "visible" array, draw with "light" colors.
        If not visible but in "explored" array, then draw it with "dark" colors.
        Otherwise, default is "SHROUD"
        """
        console.tiles_rgb[0:self.width, 0:self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD
        )
