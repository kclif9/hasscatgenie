"""Support for CatGenie switches."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from catgenie import CatGenieClient, Device

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CatGenieConfigEntry, CatGenieDeviceCoordinator
from .entity import CatGenieEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CatGenieSwitchDescription(SwitchEntityDescription):
    """Describe a CatGenie switch."""

    value_fn: Callable[[Device], bool]
    turn_on_fn: Callable[[CatGenieClient, str], Coroutine[Any, Any, Any]]
    turn_off_fn: Callable[[CatGenieClient, str], Coroutine[Any, Any, Any]]


SWITCH_DESCRIPTIONS: tuple[CatGenieSwitchDescription, ...] = (
    CatGenieSwitchDescription(
        key="child_lock",
        translation_key="child_lock",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: device.configuration.child_lock == 1,
        turn_on_fn=lambda client, device_id: client.set_child_lock(device_id, True),
        turn_off_fn=lambda client, device_id: client.set_child_lock(device_id, False),
    ),
    CatGenieSwitchDescription(
        key="extra_dry",
        translation_key="extra_dry",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: device.configuration.extra_dry,
        turn_on_fn=lambda client, device_id: client.set_extra_dry(device_id, True),
        turn_off_fn=lambda client, device_id: client.set_extra_dry(device_id, False),
    ),
    CatGenieSwitchDescription(
        key="extra_wash",
        translation_key="extra_wash",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: (
            device.configuration.binary_elements.extra_wash
            if device.configuration.binary_elements
            else False
        ),
        turn_on_fn=lambda client, device_id: client.set_extra_wash(device_id, True),
        turn_off_fn=lambda client, device_id: client.set_extra_wash(device_id, False),
    ),
    CatGenieSwitchDescription(
        key="extra_shake",
        translation_key="extra_shake",
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda device: (
            device.configuration.binary_elements.extra_shake
            if device.configuration.binary_elements
            else False
        ),
        turn_on_fn=lambda client, device_id: client.set_extra_shake(device_id, True),
        turn_off_fn=lambda client, device_id: client.set_extra_shake(device_id, False),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie switches based on a config entry."""
    async_add_entities(
        CatGenieSwitchEntity(coordinator, description)
        for coordinator in entry.runtime_data.device_coordinators.values()
        for description in SWITCH_DESCRIPTIONS
    )


class CatGenieSwitchEntity(CatGenieEntity, SwitchEntity):
    """Defines a CatGenie switch."""

    entity_description: CatGenieSwitchDescription

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(
            self.coordinator.client, self.coordinator.device_id
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(
            self.coordinator.client, self.coordinator.device_id
        )
        await self.coordinator.async_request_refresh()
