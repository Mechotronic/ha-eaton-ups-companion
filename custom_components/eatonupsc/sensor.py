from typing import Callable, Any
from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfTemperature, EntityCategory
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
    SensorEntityDescription
)

from eaton_ups_companion.models import EUCResponse

from .const import DOMAIN
from .coordinator import EatonUPSCoordinator
from .base import EatonUPSDataEntity

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class EatonUPSSensorEntityDescription(SensorEntityDescription):
    """Describes Panasonic sensor entity."""
    get_state: Callable[[EUCResponse], Any] = None
    is_available: Callable[[EUCResponse], bool] = None
SENSOR_DESCRIPTIONS = [
    EatonUPSSensorEntityDescription(
        key = "output_power",
        name="Output power",
        icon="mdi:flash",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.outputPower,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "nominal_power",
        name="Nominal power",
        icon="mdi:flash",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.nominalPower,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "energy",
        name="Energy",
        icon="mdi:flash",
        native_unit_of_measurement="kWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        get_state=lambda data: data.status.energy / 3600000,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "output_load_level",
        name="Load",
        icon="mdi:percent-box-outline",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.outputLoadLevel,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "battery_charge",
        name="Battery charge",
        icon="mdi:percent-box-outline",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.batteryCapacity,
        is_available=lambda data: True
    )
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []  # Define your sensor entities here
    for description in SENSOR_DESCRIPTIONS:
        entities.append(EatonUPSSensorEntity(coordinator, description))

    async_add_entities(entities)



class EatonUPSSensorEntity(EatonUPSDataEntity, SensorEntity):
    
    entity_description: EatonUPSSensorEntityDescription

    def __init__(self, coordinator: EatonUPSCoordinator, description: EatonUPSSensorEntityDescription):
        self.entity_description = description
        super().__init__(coordinator, description.key)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.entity_description.is_available(self.coordinator.data)

    def _async_update_attrs(self) -> None:
        """Update the attributes of the sensor."""
        self._attr_available = self.entity_description.is_available(self.coordinator.data)
        self._attr_native_value = self.entity_description.get_state(self.coordinator.data)