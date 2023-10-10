from typing import Tuple

import numpy as np

# Tile graphics structured type compatible with Console.tiles_rgb
grapic_dt = np.dtype(
    [
        ("ch", np.int32), # Unicode codepoint
        ("fg", "3B"), # 3 unsigned bytes, for RGB colors
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data
tile_dt = np.dtype(
    [
        ("walkable", np.bool_), # True if tile can be walked over
        ("transparent", np.bool_), # True if tile doesn't block FOV
        ("dark", grapic_dt), # Graphics for when tile not in FOV
        ("light", grapic_dt), # Graphics for when tile is in FOV
    ]
)


def new_tile(
        *, # Enforce use of keywords so parameter order does not matter
        walkable: int,
        transparent: int,
        dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
        light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tyle types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=grapic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(" "), (255, 255, 255), (50, 45, 15)),
    light=(ord(" "), (255, 255, 255), (95, 70, 20)),
)

wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("█"), (255, 255, 255), (20, 20, 20)),
    light=(ord("█"), (255, 255, 255), (45, 45, 45)),
)
