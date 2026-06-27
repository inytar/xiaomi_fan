"""Light platform for the Xiaomi Fan indicator LED."""

import logging

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import EntityCategory

from .const import DATA_KEY
from .fan import (
    ATTR_LED,
    FEATURE_SET_LED,
    FEATURE_SET_LED_BRIGHTNESS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up fan LED light from a config entry."""
    host = entry.data[CONF_HOST]
    fan_entity = hass.data.get(DATA_KEY, {}).get(host)
    if fan_entity is None:
        _LOGGER.warning("Fan entity not found for host %s, skipping lights", host)
        return

    if fan_entity._device_features & (FEATURE_SET_LED | FEATURE_SET_LED_BRIGHTNESS):
        async_add_entities([XiaomiFanLedLight(fan_entity)])


class XiaomiFanLedLight(LightEntity):
    """Light entity for the fan's indicator LED."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "led"
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, fan_entity):
        """Initialize the LED light entity."""
        self._fan_entity = fan_entity
        self._attr_unique_id = f"{fan_entity.unique_id}_led"
        self._attr_device_info = fan_entity.device_info

    @property
    def available(self):
        """Return true if the fan entity is available."""
        return self._fan_entity.available

    @property
    def is_on(self):
        """Return true if the LED is on."""
        return self._fan_entity._state_attrs.get(ATTR_LED)

    async def async_turn_on(self, **kwargs):
        """Turn the LED on."""
        await self._fan_entity.async_set_led_brightness(0)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the LED off."""
        await self._fan_entity.async_set_led_brightness(2)
        self.async_write_ha_state()

    async def async_update(self):
        """State is read from the fan entity's cached attributes on every poll."""
