from __future__ import annotations

import math
from typing import List, Tuple, TYPE_CHECKING

import color
import tcod.constants

if TYPE_CHECKING:
    from tcod.console import Console
    from engine import Engine
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""
    
    names = ", ".join(
        entity.name for entity in game_map.entities if entity.x == x and entity.y == y
    )

    return names.capitalize()


def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(
        x=0, y=45, width=total_width, height=1, ch=1, bg=color.bar_empty
    )

    if bar_width > 0:
        console.draw_rect(
            x=0, y=45, width=bar_width, height=1, ch=1, bg=color.bar_filled
        )

    console.print(
        x=1, y=45, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )


def render_names_at_mouse_location(
        console: Console, x: int, y: int, engine: Engine
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )


    console.print(x=x, y=y, string=names_at_mouse_location)


def render_lightning(
    console: Console, path: List[Tuple[int, int]]
) -> None:
    # TODO iterate through path and draw line based on direction
    pass

def render_circle_frame(
    console: Console, center_x: int, center_y: int, radius: float
) -> None:
    top_edge = math.ceil(center_y - radius - 1)
    bottom_edge = math.floor(center_y + radius + 1)
    left_edge = math.ceil(center_x - radius - 1)
    right_edge = math.floor(center_x + radius + 1)
    sideLen = 0
    for y in range(top_edge, bottom_edge + 1):
        dy = y - center_y
        dx = math.sqrt(abs((radius + 1)**2 - dy**2))
        left = math.ceil(center_x - dx)
        right = math.floor(center_x + dx)
        if y == top_edge:
            for x in range(left, right + 1):
                if x == left:
                    # TODO: complete circle frame drawing
                    console.print(x, y, "┌", color.red)
                elif x == right:
                    console.print(x, y, "┐", color.red)
                else:
                    console.print(x, y, "─", color.red)
                sideLen += 1
        elif y == bottom_edge:
            for x in range(left, right + 1):
                if x == left:
                    console.print(x, y, "└", color.red)
                elif x == right:
                    console.print(x, y, "┘", color.red)
                else:
                    console.print(x, y, "─", color.red)
        elif y < center_y - sideLen / 2 + 1:
                console.print(left, y, "┌", color.red)
                console.print(left + 1, y, "┘", color.red)
                console.print(right - 1, y, "└", color.red)
                console.print(right, y, "┐", color.red)
                for x in range(left + 2, right - 1):
                    console.print(x, y, " ", None, color.red, tcod.constants.BKGND_SCREEN)
        elif y > center_y + sideLen / 2 - 1:
                console.print(left, y, "└", color.red)
                console.print(left + 1, y, "┐", color.red)
                console.print(right - 1, y, "┌", color.red)
                console.print(right, y, "┘", color.red)
                for x in range(left + 2, right - 1):
                    console.print(x, y, " ", None, color.red, tcod.constants.BKGND_SCREEN)
        else:
            console.print(left, y, "│", color.red)
            console.print(right, y, "│", color.red)
            for x in range(left + 1, right):
                console.print(x, y, " ", None, color.red, tcod.constants.BKGND_SCREEN)
            

def inside_circle(
    center_x: int, center_y: int, tile_x: int, tile_y: int, radius: float
) -> bool:
    dx = center_x - tile_x
    dy = center_y - tile_y
    distance_squared = dx * dx + dy * dy
    return distance_squared <= radius * radius
