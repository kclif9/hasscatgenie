"""Support for CatGenie selects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catgenie import CleaningMode, Device

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CatGenieConfigEntry, CatGenieDeviceCoordinator
from .entity import CatGenieEntity

PARALLEL_UPDATES = 1

CLEANING_MODE_OPTIONS = ["automatic", "manual"]
CLEANING_MODE_TO_ENUM = {
    "automatic": CleaningMode.AUTOMATIC,
    "manual": CleaningMode.MANUAL,
}
CLEANING_MODE_FROM_ENUM = {v: k for k, v in CLEANING_MODE_TO_ENUM.items()}


@dataclass(frozen=True, kw_only=True)
class CatGenieSelectDescription(SelectEntityDescription):
    """Describe a CatGenie select."""


SELECT_DESCRIPTIONS: tuple[CatGenieSelectDescription, ...] = (
    CatGenieSelectDescription(
        key="cleaning_mode",
        translation_key="cleaning_mode",
        entity_category=EntityCategory.CONFIG,
        options=CLEANING_MODE_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CatGenieConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up CatGenie selects based on a config entry."""
    async_add_entities(
        CatGenieSelectEntity(coordinator, description)
        for coordinator in entry.runtime_data.device_coordinators.values()
        for description in SELECT_DESCRIPTIONS
    )


class CatGenieSelectEntity(CatGenieEntity, SelectEntity):
    """Defines a CatGenie select."""

    entity_description: CatGenieSelectDescription

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        mode = self.coordinator.data.configuration.mode
        return CLEANING_MODE_FROM_ENUM.get(mode)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        mode = CLEANING_MODE_TO_ENUM[option]
        await self.coordinator.client.set_cleaning_mode(
            self.coordinator.device_id, mode
        )
        await self.coordinator.async_request_refresh()
