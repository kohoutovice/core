"""Support for Ezviz sensors."""
from __future__ import annotations

import logging

from pyezviz.constants import SensorType

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_COORDINATOR, DOMAIN, MANUFACTURER
from .coordinator import EzvizDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Ezviz sensors based on a config entry."""
    coordinator: EzvizDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]
    sensors = []

    for idx, camera in enumerate(coordinator.data):
        for name in camera:
            # Only add sensor with value.
            if camera.get(name) is None:
                continue

            if name in SensorType.__members__:
                sensor_type_name = getattr(SensorType, name).value
                sensors.append(EzvizSensor(coordinator, idx, name, sensor_type_name))

    async_add_entities(sensors)


class EzvizSensor(CoordinatorEntity, Entity):
    """Representation of a Ezviz sensor."""

    coordinator: EzvizDataUpdateCoordinator

    def __init__(
        self,
        coordinator: EzvizDataUpdateCoordinator,
        idx: int,
        name: str,
        sensor_type_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._idx = idx
        self._camera_name = self.coordinator.data[self._idx]["name"]
        self._name = name
        self._sensor_name = f"{self._camera_name}.{self._name}"
        self.sensor_type_name = sensor_type_name
        self._serial = self.coordinator.data[self._idx]["serial"]

    @property
    def name(self) -> str:
        """Return the name of the Ezviz sensor."""
        return self._name

    @property
    def native_value(self) -> int | str:
        """Return the state of the sensor."""
        return self.coordinator.data[self._idx][self._name]

    @property
    def unique_id(self) -> str:
        """Return the unique ID of this sensor."""
        return f"{self._serial}_{self._sensor_name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device_info of the device."""
        return {
            "identifiers": {(DOMAIN, self._serial)},
            "name": self.coordinator.data[self._idx]["name"],
            "model": self.coordinator.data[self._idx]["device_sub_category"],
            "manufacturer": MANUFACTURER,
            "sw_version": self.coordinator.data[self._idx]["version"],
        }

    @property
    def device_class(self) -> str:
        """Device class for the sensor."""
        return self.sensor_type_name
