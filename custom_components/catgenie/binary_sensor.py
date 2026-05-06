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
from .entity import CatGenieEntity, CatGenieEntityDescription

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class CatGenieBinarySensorDescription(
    CatGenieEntityDescription, BinarySensorEntityDescription
):
    """Describe a CatGenie binary sensor."""

    value_fn: Callable[[Device], bool]
    attributes_fn: Callable[[Device], dict[str, str] | None] = lambda _: None


BINARY_SENSOR_DESCRIPTIONS: tuple[CatGenieBinarySensorDescription, ...] = (
    CatGenieBinarySensorDescription(
        key="status",
        translation_key="status",
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda device: device.is_cleaning,
    ),
    CatGenieBinarySensorDescription(
        key="problem",
        translation_key="problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda device: len(device.active_errors) > 0,
    ),
    CatGenieBinarySensorDescription(
        key="heater_fault",
        translation_key="heater_fault",
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
    CatGenieBinarySensorDescription(
        key="operation_error",
        translation_key="operation_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda device: bool(device.operation_status.error),
        attributes_fn=lambda device: (
            {"error": device.operation_status.error}
            if device.operation_status.error
            else None
        ),
    ),
    CatGenieBinarySensorDescription(
        key="network_type",
        translation_key="network_type",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda device: (device.connection_mode or "").lower() == "wifi",
        attributes_fn=lambda device: (
            {"network_type": device.connection_mode}
            if device.connection_mode
            else None
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie binary sensors based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    known_device_ids: set[str] = set()

    def _async_add_new_devices() -> None:
        """Add entities for any newly discovered devices."""
        new_device_ids = set(coordinator.data) - known_device_ids
        if new_device_ids:
            async_add_entities(
                CatGenieBinarySensorEntity(coordinator, description, device_id)
                for device_id in new_device_ids
                for description in BINARY_SENSOR_DESCRIPTIONS
            )
            known_device_ids.update(new_device_ids)

    _async_add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_devices))


class CatGenieBinarySensorEntity(CatGenieEntity, BinarySensorEntity):
    """Defines a CatGenie binary sensor."""

    entity_description: CatGenieBinarySensorDescription

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if (device := self.device_data) is None:
            return False
        return self.entity_description.value_fn(device)

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Return additional state attributes."""
        if (device := self.device_data) is None:
            return None
        return self.entity_description.attributes_fn(device)
