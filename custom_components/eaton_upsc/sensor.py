from typing import Callable, Any
from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import (
    ATTR_MANUFACTURER,
    ATTR_MODEL,
    ATTR_SERIAL_NUMBER,
    ATTR_SW_VERSION,
    PERCENTAGE,
    STATE_UNKNOWN,
    EntityCategory,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfEnergy,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
    SensorEntityDescription
)

from eaton_ups_companion.models import EUCResponse

from .const import (
    DOMAIN,
    STATUS_ON_BATTERY,
    STATUS_ON_UTILITY,
    UPS_STATUS
    )
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
        key = "status",
        name="Status",
        device_class=SensorDeviceClass.ENUM,
        options=UPS_STATUS,
        get_state=lambda data: STATUS_ON_UTILITY if data.status.acPresent else STATUS_ON_BATTERY,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "output_power",
        name="Output power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.outputPower,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "nominal_power",
        name="Nominal power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.nominalPower,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "energy",
        name="Energy",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        get_state=lambda data: round(data.status.energy / 3600000,2),
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "output_load_level",
        name="Load",
        icon="mdi:percent-box-outline",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.outputLoadLevel,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "output_voltage",
        name="Output voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.powerSourceCfg.outputVoltage,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "battery_charge",
        name="Battery charge",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        get_state=lambda data: data.status.batteryCapacity,
        is_available=lambda data: True
    ),
    EatonUPSSensorEntityDescription(
        key = "battery_runtime",
        name="Battery runtime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        get_state=lambda data: data.status.batteryRunTime,
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