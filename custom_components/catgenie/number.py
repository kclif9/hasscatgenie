"""Support for CatGenie numbers."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from catgenie import CatGenieClient, Device

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CatGenieConfigEntry
from .entity import CatGenieEntity, CatGenieEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CatGenieNumberDescription(CatGenieEntityDescription, NumberEntityDescription):
    """Describe a CatGenie number."""

    value_fn: Callable[[Device], float | None]
    set_fn: Callable[[CatGenieClient, str, int], Coroutine[Any, Any, Any]]


NUMBER_DESCRIPTIONS: tuple[CatGenieNumberDescription, ...] = (
    CatGenieNumberDescription(
        key="volume_level",
        translation_key="volume_level",
        entity_category=EntityCategory.CONFIG,
        native_min_value=1,
        native_max_value=7,
        native_step=1,
        mode=NumberMode.SLIDER,
        value_fn=lambda device: device.configuration.volume_level,
        set_fn=lambda client, device_id, value: client.set_volume(device_id, value),
    ),
    CatGenieNumberDescription(
        key="cat_delay",
        translation_key="cat_delay",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=3600,
        native_step=60,
        mode=NumberMode.BOX,
        value_fn=lambda device: device.configuration.cat_delay,
        set_fn=lambda client, device_id, value: client.set_cat_delay(
            device_id, value
        ),
    ),
    CatGenieNumberDescription(
        key="cat_sensitivity",
        translation_key="cat_sensitivity",
        entity_category=EntityCategory.CONFIG,
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        mode=NumberMode.BOX,
        value_fn=lambda device: device.configuration.cat_sense,
        set_fn=lambda client, device_id, value: client.set_cat_sensitivity(
            device_id, value
        ),
    ),
    CatGenieNumberDescription(
        key="auto_lock_delay",
        translation_key="auto_lock_delay",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_min_value=0,
        native_max_value=3600,
        native_step=60,
        mode=NumberMode.BOX,
        value_fn=lambda device: device.configuration.auto_lock,
        set_fn=lambda client, device_id, value: client.set_auto_lock(
            device_id, value
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie numbers based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    known_device_ids: set[str] = set()

    def _async_add_new_devices() -> None:
        """Add entities for any newly discovered devices."""
        new_device_ids = set(coordinator.data) - known_device_ids
        if new_device_ids:
            async_add_entities(
                CatGenieNumberEntity(coordinator, description, device_id)
                for device_id in new_device_ids
                for description in NUMBER_DESCRIPTIONS
            )
            known_device_ids.update(new_device_ids)

    _async_add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_devices))


class CatGenieNumberEntity(CatGenieEntity, NumberEntity):
    """Defines a CatGenie number."""

    entity_description: CatGenieNumberDescription

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if (device := self.device_data) is None:
            return None
        return self.entity_description.value_fn(device)

    async def async_set_native_value(self, value: float) -> None:
        """Set the number value."""
        await self.entity_description.set_fn(
            self.coordinator.client, self._device_id, round(value)
        )
        await self.coordinator.async_request_refresh()
