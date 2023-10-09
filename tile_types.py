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
        ("dark", grapic_dt) # Graphics for when tile not in FOV
    ]
)


def new_tile(
        *, # Enforce use of keywords so parameter order does not matter
        walkable: int,
        transparent: int,
        dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tyle types"""
    return np.array((walkable, transparent, dark), dtype=tile_dt)


floor = new_tile(
    walkable=True, transparent=True, dark=(ord(" "), (65, 45, 75), (50, 45, 35)),
)

wall = new_tile(
    walkable=False, transparent=False, dark=(ord("█"), (85, 85, 75), (10, 10, 10)),
)