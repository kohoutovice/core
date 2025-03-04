"""Support for the Forecast.Solar sensor service."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_IDENTIFIERS, ATTR_MANUFACTURER, ATTR_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import ATTR_ENTRY_TYPE, DOMAIN, ENTRY_TYPE_SERVICE, SENSORS
from .models import ForecastSolarSensorEntityDescription


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Defer sensor setup to the shared sensor module."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        ForecastSolarSensorEntity(
            entry_id=entry.entry_id,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in SENSORS
    )


class ForecastSolarSensorEntity(CoordinatorEntity, SensorEntity):
    """Defines a Forcast.Solar sensor."""

    entity_description: ForecastSolarSensorEntityDescription

    def __init__(
        self,
        *,
        entry_id: str,
        coordinator: DataUpdateCoordinator,
        entity_description: ForecastSolarSensorEntityDescription,
    ) -> None:
        """Initialize Forcast.Solar sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self.entity_id = f"{SENSOR_DOMAIN}.{entity_description.key}"
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"

        self._attr_device_info = {
            ATTR_IDENTIFIERS: {(DOMAIN, entry_id)},
            ATTR_NAME: "Solar Production Forecast",
            ATTR_MANUFACTURER: "Forecast.Solar",
            ATTR_ENTRY_TYPE: ENTRY_TYPE_SERVICE,
        }

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        if self.entity_description.state is None:
            state: StateType | datetime = getattr(
                self.coordinator.data, self.entity_description.key
            )
        else:
            state = self.entity_description.state(self.coordinator.data)

        if isinstance(state, datetime):
            return state.isoformat()
        return state
