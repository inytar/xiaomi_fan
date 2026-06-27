"""Button platform for Xiaomi Fan directional movement controls."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.const import CONF_HOST

from .const import DATA_KEY
from .fan import FEATURE_SET_VERTICAL_OSCILLATION_ANGLE, FEATURE_TURN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up fan movement buttons from a config entry."""
    host = entry.data[CONF_HOST]
    fan_entity = hass.data.get(DATA_KEY, {}).get(host)
    if fan_entity is None:
        _LOGGER.warning("Fan entity not found for host %s, skipping buttons", host)
        return

    if not (fan_entity._device_features & FEATURE_TURN):
        return

    entities = [
        XiaomiFanMoveButton(fan_entity, "left"),
        XiaomiFanMoveButton(fan_entity, "right"),
    ]
    if fan_entity._device_features & FEATURE_SET_VERTICAL_OSCILLATION_ANGLE:
        entities += [
            XiaomiFanMoveButton(fan_entity, "up"),
            XiaomiFanMoveButton(fan_entity, "down"),
        ]

    async_add_entities(entities)


class XiaomiFanMoveButton(ButtonEntity):
    """Button entity that nudges the fan in one direction."""

    _attr_has_entity_name = True

    def __init__(self, fan_entity, direction: str):
        """Initialize the move button."""
        self._fan_entity = fan_entity
        self._direction = direction
        self._attr_translation_key = f"move_{direction}"
        self._attr_unique_id = f"{fan_entity.unique_id}_move_{direction}"
        self._attr_device_info = fan_entity.device_info

    @property
    def available(self):
        """Return true if the fan entity is available."""
        return self._fan_entity.available

    async def async_press(self) -> None:
        """Send the move command to the fan."""
        await self._fan_entity.async_turn(self._direction)
