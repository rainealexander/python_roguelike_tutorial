from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import color
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Attempt to return action for this item"""
        return actions.ItemAction(consumer, self.parent)
    
    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this item's ability
        `action` is the context for activation
        """
        raise NotImplementedError()
    
    def consume(self) -> None:
        """Remove consumed item from containing inventory"""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You consume the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"You are at full health.")


class LightningDamageConsumable(Consumable):
    def __init__(self, damage: int, max_range: int):
        self.damage = damage
        self.max_range = max_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.max_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)
                if distance < closest_distance:
                    target = actor
                    closest_distance = distance
        if target:
            # TODO: figure out how to render lightning bolt
            # path = consumer.ai.get_path_to(target)
            # render_functions.render_lightning()
            self.engine.message_log.add_message(
                f"A lightning bolt strickes the {target.name} with a loud thunder, for {self.damage} damage!"
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise Impossible("No enemy is close enough to strike")
        