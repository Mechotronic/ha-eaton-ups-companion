import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from eaton_ups_companion import EUCClient
from .const import DOMAIN, DEFAULT_PORT, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


# Define a configuration schema.
DATA_SCHEMA = vol.Schema(
    {
        vol.Required(
            CONF_HOST, 
            description={"suggestion": "The IP address or hostname of your Eaton UPS Companion server."}
        ): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class EatonUPSCompanionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eaton UPS Companion."""
    
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors = {}

        if user_input is not None:
            host = user_input.get(CONF_HOST)
            port = user_input.get(CONF_PORT)
            scan_interval = user_input.get("scan_interval")

            # Validate connection using EUCClient.
            client = EUCClient(f"http://{host}:{port}/euc-data.js")
            try:
                await client.fetch_data()
            except Exception as err:
                _LOGGER.error("Error connecting to Eaton UPS Companion at %s:%s: %s", host, port, err)
                errors["base"] = "cannot_connect"
            else:
                # If validation passes, create the config entry
                return self.async_create_entry(title="Eaton UPS Companion", data=user_input)

        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors
        )
