"""Frontend registration for the DIVA custom panel."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import (
    CONF_SHOW_EDITOR_IN_SIDEBAR,
    DEFAULT_SHOW_EDITOR_IN_SIDEBAR,
    DOMAIN,
    FRONTEND_MODULE_URL,
    FRONTEND_PANEL_COMPONENT,
    FRONTEND_PANEL_ICON,
    FRONTEND_PANEL_TITLE,
    FRONTEND_PANEL_URL_PATH,
    FRONTEND_STATIC_BASE,
)

_FRONTEND_REGISTERED = "frontend_registered"
_FRONTEND_STATIC_REGISTERED = "frontend_static_registered"


async def async_setup_frontend(hass: HomeAssistant) -> None:
    """Register DIVA frontend assets and the editor panel."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    frontend_dir = Path(__file__).resolve().parent / "frontend"

    if not domain_data.get(_FRONTEND_STATIC_REGISTERED):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(FRONTEND_STATIC_BASE, str(frontend_dir), True)]
        )
        domain_data[_FRONTEND_STATIC_REGISTERED] = True

    frontend.async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title=FRONTEND_PANEL_TITLE,
        sidebar_icon=FRONTEND_PANEL_ICON,
        frontend_url_path=FRONTEND_PANEL_URL_PATH,
        config={
            "integration": DOMAIN,
            "_panel_custom": {
                "name": FRONTEND_PANEL_COMPONENT,
                "module_url": FRONTEND_MODULE_URL,
                "embed_iframe": False,
                "trust_external": False,
            },
        },
        require_admin=True,
        update=True,
        show_in_sidebar=_show_editor_in_sidebar(hass),
    )
    domain_data[_FRONTEND_REGISTERED] = True


async def async_unload_frontend(hass: HomeAssistant) -> None:
    """Remove the DIVA frontend panel when the last entry unloads."""
    domain_data = hass.data.get(DOMAIN, {})
    if domain_data.get(_FRONTEND_REGISTERED):
        frontend.async_remove_panel(hass, FRONTEND_PANEL_URL_PATH, warn_if_unknown=False)
        domain_data[_FRONTEND_REGISTERED] = False


def _show_editor_in_sidebar(hass: HomeAssistant) -> bool:
    """Return whether the DIVA editor should be visible in the sidebar."""
    entries = hass.config_entries.async_entries(DOMAIN)
    if not entries:
        return DEFAULT_SHOW_EDITOR_IN_SIDEBAR

    entry = entries[0]
    if CONF_SHOW_EDITOR_IN_SIDEBAR in entry.options:
        return bool(entry.options[CONF_SHOW_EDITOR_IN_SIDEBAR])
    return bool(entry.data.get(CONF_SHOW_EDITOR_IN_SIDEBAR, DEFAULT_SHOW_EDITOR_IN_SIDEBAR))
