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
from .entity import CatGenieEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CatGenieButtonDescription(ButtonEntityDescription):
    """Describe a CatGenie button."""


BUTTON_DESCRIPTIONS: tuple[CatGenieButtonDescription, ...] = (
    CatGenieButtonDescription(
        key="start_clean",
        translation_key="start_clean",
        device_class=ButtonDeviceClass.IDENTIFY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie buttons based on a config entry."""
    async_add_entities(
        CatGenieButtonEntity(coordinator, description)
        for coordinator in entry.runtime_data.device_coordinators.values()
        for description in BUTTON_DESCRIPTIONS
    )


class CatGenieButtonEntity(CatGenieEntity, ButtonEntity):
    """Defines a CatGenie button."""

    entity_description: CatGenieButtonDescription

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.client.start_cleaning(self.coordinator.device_id)
        await self.coordinator.async_request_refresh()
