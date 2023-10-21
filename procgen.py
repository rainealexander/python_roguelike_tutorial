from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine


class RectangularRoom:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    
    @property
    def center(self) -> Tuple[int, int]:
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)

        return center_x, center_y
    

    @property
    def inner(self) -> Tuple[slice, slice]:
        """Return the inner area of this room as a 2d array index"""
        return slice(self.x1 + 1, self.x2), slice(self.y1 +1, self.y2)
    
    def intersects(self, other: RectangularRoom) -> bool:
        """Return true if this room overlaps with another of the same type"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def place_entities(
        room: RectangularRoom, dungeon: GameMap, max_monsters: int, max_items: int
) -> None:
    number_of_monsters = random.randint(0, max_monsters)
    number_of_items = random.randint(0, max_items)

    for i in range(number_of_monsters):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            if random.random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x = random.randint(room.x1 + 1, room.x2 - 1)
        y = random.randint(room.y1 + 1, room.y2 - 1)

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
            entity_factories.health_potion.spawn(dungeon, x, y)


def tunnel_between(
        start: Tuple[int, int], end: Tuple[int, int]
) -> Iterator[Tuple[int, int]]:
    """Return an L-shaped tunnel between two points"""
    x1, y1 = start
    x2, y2 = end
    if random.random() < 0.5: # 50/50
        # tunnel horizontal then vertical
        corner_x, corner_y = x2, y1
    else:
        # tunnel vertical then horizontal
        corner_x, corner_y = x1, y2
    
    # Generate coordinates for tunnel
    for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
        yield x, y
    for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
        yield x, y

    

def generate_dungeon(
        max_rooms: int,
        room_min_size: int,
        room_max_size: int,
        map_width: int,
        map_height: int,
        max_monsters_per_room: int,
        max_items_per_room: int,
        engine: Engine
) -> GameMap:
    """Generate a new dungeon map"""
    player = engine.player
    dungeon = GameMap(engine, map_width, map_height, entities=[player])

    rooms: List[RectangularRoom] = []

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        new_room = RectangularRoom(x, y, room_width, room_height)

        # Check if new room intersects any existing room
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # room intersects, go to next attempt
        # no intersections, proceed

        # Dig out room inner area
        dungeon.tiles[new_room.inner] = tile_types.floor

        if len(rooms) == 0:
            # First room, set player coords
            player.place(*new_room.center, dungeon)
        else:
            # Dig tunnel between this and previous room
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x,y] = tile_types.floor
        
        place_entities(new_room, dungeon, max_monsters_per_room, max_items_per_room)

        # Append new room to list
        rooms.append(new_room)

    return dungeon

