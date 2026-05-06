"""Support for CatGenie selects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from catgenie import CleaningMode, Device

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import CatGenieConfigEntry
from .entity import CatGenieEntity, CatGenieEntityDescription

PARALLEL_UPDATES = 1

CLEANING_MODE_OPTIONS = ["automatic", "manual"]
CLEANING_MODE_TO_ENUM = {
    "automatic": CleaningMode.AUTOMATIC,
    "manual": CleaningMode.MANUAL,
}
CLEANING_MODE_FROM_ENUM = {v: k for k, v in CLEANING_MODE_TO_ENUM.items()}


@dataclass(frozen=True, kw_only=True)
class CatGenieSelectDescription(CatGenieEntityDescription, SelectEntityDescription):
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
    coordinator = entry.runtime_data.coordinator
    known_device_ids: set[str] = set()

    def _async_add_new_devices() -> None:
        """Add entities for any newly discovered devices."""
        new_device_ids = set(coordinator.data) - known_device_ids
        if new_device_ids:
            async_add_entities(
                CatGenieSelectEntity(coordinator, description, device_id)
                for device_id in new_device_ids
                for description in SELECT_DESCRIPTIONS
            )
            known_device_ids.update(new_device_ids)

    _async_add_new_devices()
    entry.async_on_unload(coordinator.async_add_listener(_async_add_new_devices))


class CatGenieSelectEntity(CatGenieEntity, SelectEntity):
    """Defines a CatGenie select."""

    entity_description: CatGenieSelectDescription

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if (device := self.device_data) is None:
            return None
        mode = device.configuration.mode
        return CLEANING_MODE_FROM_ENUM.get(mode)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option not in CLEANING_MODE_TO_ENUM:
            raise ValueError(
                f"Unsupported option '{option}', must be one of: {CLEANING_MODE_OPTIONS}"
            )
        mode = CLEANING_MODE_TO_ENUM[option]
        await self.coordinator.client.set_cleaning_mode(self._device_id, mode)
        await self.coordinator.async_request_refresh()
