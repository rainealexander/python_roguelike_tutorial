from __future__ import annotations

import random
from typing import Iterator, List, Tuple, TYPE_CHECKING

import numpy as np
import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine


COLUMN_ROOM_CHANCE = 0.6
IRREGULAR_ROOM_CHANCE = 0.5
SPAWN_ATTEMPTS = 5

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
        return slice(self.x1 + 1, self.x2), slice(self.y1 + 1, self.y2)
    
    def intersects(self, other: RectangularRoom) -> bool:
        """Return true if this room overlaps with another of the same type"""
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )
    
    def dig_room(self, dungeon: GameMap) -> None:
        # Dig out room inner area
        dungeon.tiles[self.inner] = tile_types.floor


class IrregularRoom(RectangularRoom):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.width = width
        self.height = height


    @property
    def center(self) -> Tuple[int, int]:
        return super().center

    @property
    def inner(self) -> Tuple[slice, slice]:
        return super().inner

    def dig_room(self, dungeon: GameMap) -> None:
        # Dig out room inner area
        for x in range(self.x1, self.x2):
            for y in range(self.y1, self.y2):
                if x % self.width // 3 == 0 and y % self.height // 3 == 0:
                    continue
                else:
                    dungeon.tiles[x, y] = tile_types.floor


class ColumnRoom(RectangularRoom):
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.width = width
        self.height = height

    @property
    def center(self) -> Tuple[int, int]:
        return super().center

    @property
    def inner(self) -> Tuple[slice, slice]:
        return super().inner

    def dig_room(self, dungeon: GameMap) -> None:
        # Dig out room inner area
        for x in range(self.x1 + 2, self.x2 - 2):
            for y in range(self.y1 + 2, self.y2 - 2):
                if x % 2 == 0 and y % 2 == 0:
                    continue
                else:
                    dungeon.tiles[x, y] = tile_types.floor


def place_entities(
        room: RectangularRoom, dungeon: GameMap, max_monsters: int, max_items: int
) -> None:
    number_of_monsters = random.randint(0, max_monsters)
    number_of_items = random.randint(0, max_items)

    spawnable = np.array(dungeon.tiles["walkable"], dtype=np.int8)

    for i in range(number_of_monsters):
        x, y, counter = 0, 0, 0
        
        while not spawnable[x, y] and counter < SPAWN_ATTEMPTS:
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            counter += 1

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities) and spawnable[x, y]:
            if random.random() < 0.8:
                entity_factories.orc.spawn(dungeon, x, y)
            else:
                entity_factories.troll.spawn(dungeon, x, y)

    for i in range(number_of_items):
        x, y, counter = 0, 0, 0
        
        while not spawnable[x, y] and counter < SPAWN_ATTEMPTS:
            x = random.randint(room.x1 + 1, room.x2 - 1)
            y = random.randint(room.y1 + 1, room.y2 - 1)
            counter += 1

        if not any(entity.x == x and entity.y == y for entity in dungeon.entities) and spawnable[x, y]:
            item_chance = random.random()

            if item_chance < 0.4:
                entity_factories.health_potion.spawn(dungeon, x, y)
            elif item_chance < 0.8:
                entity_factories.fireball_scroll.spawn(dungeon, x, y)
            elif item_chance < 0.89:
                entity_factories.confusion_scroll.spawn(dungeon, x, y)
            else:
                entity_factories.lightning_scroll.spawn(dungeon, x, y)


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
    skip_initial_tiles = 2
    for x, y in tcod.los.bresenham((x1 , y1), (corner_x, corner_y)).tolist():
        if  skip_initial_tiles > 0:
            skip_initial_tiles -= 1
            continue
        yield x, y
    tunnel_2 = tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist()
    end_length = len(tunnel_2)
    for x, y in tunnel_2:
        end_length -= 1
        if end_length < 2:
            continue
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
    center_of_last_room = (0, 0)
    last_room: RectangularRoom

    for r in range(max_rooms):
        room_width = random.randint(room_min_size, room_max_size)
        room_height = random.randint(room_min_size, room_max_size)

        x = random.randint(0, dungeon.width - room_width - 1)
        y = random.randint(0, dungeon.height - room_height - 1)

        room_chance = random.random()
        if len(rooms) == 0:
            room_chance = 1

        if room_chance <= IRREGULAR_ROOM_CHANCE:
            new_room = IrregularRoom(x, y, room_width, room_height)

        elif room_chance <= COLUMN_ROOM_CHANCE:
            room_width += 1
            room_height += 1

            x = random.randint(0, dungeon.width - room_width - 1)
            y = random.randint(0, dungeon.height - room_height - 1)

            if room_width % 2 == 0:
                room_width += 1
            if room_height % 2 == 0:
                room_height += 1
            new_room = ColumnRoom(x, y, room_width, room_height)
            
        else:
            new_room = RectangularRoom(x, y, room_width, room_height)

        # Check if new room intersects any existing room
        if any(new_room.intersects(other_room) for other_room in rooms):
            continue # room intersects, go to next attempt
        # no intersections, proceed

        # Dig out room inner area
        new_room.dig_room(dungeon)

        if len(rooms) == 0:
            # First room, set player coords
            player.place(*new_room.center, dungeon)
        else:
            # Dig tunnel between this and previous room
            for x, y in tunnel_between(rooms[-1].center, new_room.center):
                dungeon.tiles[x,y] = tile_types.floor

            center_of_last_room = new_room.center
        
        extra_tunnel_chance = 0.15
        if random.random() <= extra_tunnel_chance and len(rooms) > 2 or r == max_rooms - 1:
            for x, y in tunnel_between(rooms[random.randint(0, len(rooms) - 1)].center, last_room.center):
                dungeon.tiles[x,y] = tile_types.floor

        place_entities(new_room, dungeon, max_monsters_per_room, max_items_per_room)

        dungeon.tiles[center_of_last_room] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room
        
        # Append new room to list
        rooms.append(new_room)
        last_room = new_room

    return dungeon

