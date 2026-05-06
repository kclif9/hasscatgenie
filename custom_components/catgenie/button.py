"""Support for CatGenie buttons."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CatGenieConfigEntry
from .entity import CatGenieEntity, CatGenieEntityDescription

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CatGenieButtonDescription(CatGenieEntityDescription, ButtonEntityDescription):
    """Describe a CatGenie button."""


BUTTON_DESCRIPTIONS: tuple[CatGenieButtonDescription, ...] = (
    CatGenieButtonDescription(
        key="start_clean",
        translation_key="start_clean",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie buttons based on a config entry."""
    coordinator = entry.runtime_data.coordinator
    known_device_ids: set[str] = set()

    def _async_add_new_devices() -> None:
        """Add entities for any newly discovered devices."""
        new_device_ids = set(coordinator.data) - known_device_ids
        if new_device_ids:
            async_add_entities(
                CatGenieButtonEntity(coordinator, description, device_id)
                for device_id in new_device_ids
                for description in BUTTON_DESCRIPTIONS
            )
            known_device_ids.update(new_device_ids)

    _async_add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_devices))


class CatGenieButtonEntity(CatGenieEntity, ButtonEntity):
    """Defines a CatGenie button."""

    entity_description: CatGenieButtonDescription

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.client.start_cleaning(self._device_id)
        await self.coordinator.async_request_refresh()
