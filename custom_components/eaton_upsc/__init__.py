"""Initialize the Eaton UPS Companion integration."""

"""Initialize the Eaton UPS Companion integration."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from eaton_ups_companion import EUCClient
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, PLATFORMS
from .coordinator import EatonUPSCoordinator

_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up Eaton UPS Companion
    """
    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    scan_interval = entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    url = f"http://{host}:{port}/euc-data.js"
    client = EUCClient(url)


    coordinator = EatonUPSCoordinator(
        hass,
        entry.data,
        host,
        client,
        update_interval=timedelta(seconds=scan_interval),
    )

    # Fetch the initial data to ensure we have valid data before sensors are set up.
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator so that both platforms and other parts of the integration
    # can access the data.
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to the sensor platform.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload a config entry.

    This function unloads the sensor platforms and cleans up any data stored in hass.data.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
