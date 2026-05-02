"""Support for CatGenie binary sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from catgenie import Device

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CatGenieConfigEntry
from .entity import CatGenieEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class CatGenieBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a CatGenie binary sensor."""

    value_fn: Callable[[Device], bool]


BINARY_SENSOR_DESCRIPTIONS: tuple[CatGenieBinarySensorDescription, ...] = (
    CatGenieBinarySensorDescription(
        key="problem",
        translation_key="problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda device: len(device.active_errors) > 0,
    ),
    CatGenieBinarySensorDescription(
        key="low_heater",
        translation_key="low_heater",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.low_heater,
    ),
    CatGenieBinarySensorDescription(
        key="fan_shutter",
        translation_key="fan_shutter",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda device: device.fan_shutter,
    ),
    CatGenieBinarySensorDescription(
        key="occupancy",
        translation_key="occupancy",
        device_class=BinarySensorDeviceClass.OCCUPANCY,
        value_fn=lambda device: device.operation_status.is_cat_detected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie binary sensors based on a config entry."""
    async_add_entities(
        CatGenieBinarySensorEntity(coordinator, description)
        for coordinator in entry.runtime_data.device_coordinators.values()
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class CatGenieBinarySensorEntity(CatGenieEntity, BinarySensorEntity):
    """Defines a CatGenie binary sensor."""

    entity_description: CatGenieBinarySensorDescription

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self.coordinator.data)
