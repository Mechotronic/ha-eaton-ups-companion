import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.entity import DeviceInfo

from eaton_ups_companion import EUCClient
from eaton_ups_companion.models import EUCResponse

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class EatonUPSCoordinator(DataUpdateCoordinator[EUCResponse]):

    def __init__(self, hass: HomeAssistant, config: dict, host: str, api_client: EUCClient, update_interval: timedelta):
        super().__init__(
            hass,
            _LOGGER,
            name="Eaton UPS Companion Data",
            update_interval=update_interval,
            update_method=self._fetch_device_data,
        )
        self._hass = hass
        self._config = config
        self._api_client = api_client
        self._data:EUCResponse = None
        self._device_id = f"euc_{host}"

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_info(self)->DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id )},
            manufacturer=self._data.sysInfo.manufacturer,
            model=f"{self._data.deviceInfo.product} {self._data.deviceInfo.model}",
            name=self._data.sysInfo.name,
            sw_version=f"{self._data.sysInfo.vMajor}.{self._data.sysInfo.vMinor}.{self._data.sysInfo.vBuild}"
        )
    
    async def _async_setup(self) -> None:
        self._data = await self._api_client.fetch_data()

    async def _fetch_device_data(self)->EUCResponse:
        try:
            await self._api_client.update_data(self._data)
            return self._data
        except BaseException as e:
            _LOGGER.error("Error fetching device data from API: %s", e, exc_info=e)
            raise UpdateFailed(f"Invalid response from API: {e}") from e