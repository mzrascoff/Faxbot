"""
Configuration system for Faxbot Phase 3.

This package contains the hierarchical configuration provider and related utilities.
It also re-exports the original config.py module contents for backward compatibility.
"""

# Import everything from the original config.py module
# Use absolute import to explicitly get the module, not this package
from ..config import (
    settings,
    reload_settings, 
    active_outbound,
    active_inbound,
    VALID_BACKENDS,
    providerHasTrait,
    providerTraitValue,
)

# Import new Phase 3 components
from .hierarchical_provider import HierarchicalConfigProvider

# Re-export everything for backward compatibility
__all__ = [
    "HierarchicalConfigProvider",
    "settings",
    "reload_settings",
    "active_outbound", 
    "active_inbound",
    "VALID_BACKENDS",
    "providerHasTrait",
    "providerTraitValue",
]