"""Switch platform for Xiaomi Fan toggles (child lock, buzzer)."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import EntityCategory

from .const import DATA_KEY, DOMAIN
from .fan import (
    ATTR_BUZZER,
    ATTR_CHILD_LOCK,
    ATTR_IONIZER,
    ATTR_VERTICAL_OSCILLATE,
    FEATURE_SET_ANION,
    FEATURE_SET_BUZZER,
    FEATURE_SET_CHILD_LOCK,
    FEATURE_SET_VERTICAL_OSCILLATION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up fan toggle switches from a config entry."""
    host = entry.data[CONF_HOST]
    fan_entity = hass.data.get(DATA_KEY, {}).get(host)
    if fan_entity is None:
        _LOGGER.warning("Fan entity not found for host %s, skipping switches", host)
        return

    entities = []
    if fan_entity._device_features & FEATURE_SET_CHILD_LOCK:
        entities.append(XiaomiFanChildLockSwitch(fan_entity))
    if fan_entity._device_features & FEATURE_SET_BUZZER:
        entities.append(XiaomiFanBuzzerSwitch(fan_entity))
    if fan_entity._device_features & FEATURE_SET_VERTICAL_OSCILLATION:
        entities.append(XiaomiFanVerticalOscillateSwitch(fan_entity))
    if fan_entity._device_features & FEATURE_SET_ANION:
        entities.append(XiaomiFanIonizerSwitch(fan_entity))

    async_add_entities(entities)


class _XiaomiFanToggleSwitch(SwitchEntity):
    """Base class for simple on/off fan switches."""

    _attr_has_entity_name = True

    def __init__(self, fan_entity, unique_id_suffix):
        self._fan_entity = fan_entity
        self._attr_unique_id = f"{fan_entity.unique_id}_{unique_id_suffix}"
        self._attr_device_info = fan_entity.device_info

    @property
    def available(self):
        return self._fan_entity.available

    async def async_update(self):
        """State is read from the fan entity's cached attributes on every poll."""


class XiaomiFanChildLockSwitch(_XiaomiFanToggleSwitch):
    """Switch entity for the fan's child lock."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "child_lock"

    def __init__(self, fan_entity):
        super().__init__(fan_entity, "child_lock")

    @property
    def is_on(self):
        return self._fan_entity._state_attrs.get(ATTR_CHILD_LOCK)

    async def async_turn_on(self, **kwargs):
        await self._fan_entity.async_set_child_lock_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._fan_entity.async_set_child_lock_off()
        self.async_write_ha_state()


class XiaomiFanBuzzerSwitch(_XiaomiFanToggleSwitch):
    """Switch entity for the fan's buzzer."""

    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "buzzer"

    def __init__(self, fan_entity):
        super().__init__(fan_entity, "buzzer")

    @property
    def is_on(self):
        return self._fan_entity._state_attrs.get(ATTR_BUZZER)

    async def async_turn_on(self, **kwargs):
        await self._fan_entity.async_set_buzzer_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._fan_entity.async_set_buzzer_off()
        self.async_write_ha_state()


class XiaomiFanVerticalOscillateSwitch(_XiaomiFanToggleSwitch):
    """Switch entity for the fan's vertical oscillation."""

    _attr_translation_key = "vertical_oscillate"

    def __init__(self, fan_entity):
        super().__init__(fan_entity, "vertical_oscillate")

    @property
    def is_on(self):
        return self._fan_entity._state_attrs.get(ATTR_VERTICAL_OSCILLATE)

    async def async_turn_on(self, **kwargs):
        await self._fan_entity.async_set_vertical_oscillation_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._fan_entity.async_set_vertical_oscillation_off()
        self.async_write_ha_state()


class XiaomiFanIonizerSwitch(_XiaomiFanToggleSwitch):
    """Switch entity for the fan's ionizer."""

    _attr_translation_key = "ionizer"

    def __init__(self, fan_entity):
        """Initialize the ionizer switch."""
        super().__init__(fan_entity, "ionizer")

    @property
    def is_on(self):
        """Return the ionizer state."""
        return self._fan_entity._state_attrs.get(ATTR_IONIZER)

    async def async_turn_on(self, **kwargs):
        """Turn the ionizer on."""
        await self._fan_entity.async_set_anion_on()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn the ionizer off."""
        await self._fan_entity.async_set_anion_off()
        self.async_write_ha_state()
