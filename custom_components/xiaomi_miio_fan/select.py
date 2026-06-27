"""Select platform for Xiaomi Fan oscillation angle controls."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_HOST

from .const import DATA_KEY
from .fan import (
    ATTR_ANGLE,
    ATTR_VERTICAL_ANGLE,
    FEATURE_SET_OSCILLATION_ANGLE,
    FEATURE_SET_VERTICAL_OSCILLATION_ANGLE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up fan oscillation angle selects from a config entry."""
    host = entry.data[CONF_HOST]
    fan_entity = hass.data.get(DATA_KEY, {}).get(host)
    if fan_entity is None:
        _LOGGER.warning("Fan entity not found for host %s, skipping selects", host)
        return

    entities = []
    if fan_entity._device_features & FEATURE_SET_OSCILLATION_ANGLE:
        entities.append(XiaomiFanOscillationAngleSelect(fan_entity))
    if fan_entity._device_features & FEATURE_SET_VERTICAL_OSCILLATION_ANGLE:
        entities.append(XiaomiFanVerticalOscillationAngleSelect(fan_entity))

    async_add_entities(entities)


class _XiaomiFanAngleSelect(SelectEntity):
    """Base class for fan angle selects."""

    _attr_has_entity_name = True

    def __init__(self, fan_entity, unique_id_suffix):
        """Initialize the select entity."""
        self._fan_entity = fan_entity
        self._attr_unique_id = f"{fan_entity.unique_id}_{unique_id_suffix}"
        self._attr_device_info = fan_entity.device_info

    @property
    def available(self):
        """Return true if the fan entity is available."""
        return self._fan_entity.available

    async def async_update(self):
        """State is read from the fan entity's cached attributes on every poll."""


class XiaomiFanOscillationAngleSelect(_XiaomiFanAngleSelect):
    """Select entity for the fan's horizontal oscillation angle."""

    _attr_translation_key = "oscillation_angle"

    def __init__(self, fan_entity):
        """Initialize the oscillation angle select."""
        super().__init__(fan_entity, "oscillation_angle")
        self._attr_options = [str(a) for a in fan_entity._oscillation_angle_options]

    @property
    def current_option(self):
        """Return the currently selected oscillation angle."""
        angle = self._fan_entity._state_attrs.get(ATTR_ANGLE)
        if angle is None:
            return None
        return str(angle)

    async def async_select_option(self, option: str) -> None:
        """Set the oscillation angle."""
        await self._fan_entity.async_set_oscillation_angle(int(option))
        self.async_write_ha_state()


class XiaomiFanVerticalOscillationAngleSelect(_XiaomiFanAngleSelect):
    """Select entity for the fan's vertical oscillation angle."""

    _attr_translation_key = "vertical_oscillation_angle"

    def __init__(self, fan_entity):
        """Initialize the vertical oscillation angle select."""
        super().__init__(fan_entity, "vertical_oscillation_angle")
        self._attr_options = [
            str(a) for a in fan_entity._vertical_oscillation_angle_options
        ]

    @property
    def current_option(self):
        """Return the currently selected vertical oscillation angle."""
        angle = self._fan_entity._state_attrs.get(ATTR_VERTICAL_ANGLE)
        if angle is None:
            return None
        return str(angle)

    async def async_select_option(self, option: str) -> None:
        """Set the vertical oscillation angle."""
        await self._fan_entity.async_set_vertical_oscillation_angle(int(option))
        self.async_write_ha_state()
