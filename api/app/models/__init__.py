"""
Database models for Faxbot Phase 3.

This package contains all database models for the hierarchical configuration
system, events, and other Phase 3 features.
"""

# Make commonly used classes available at package level
from .config import ConfigGlobal, ConfigTenant, ConfigDepartment, ConfigGroup, ConfigUser, ConfigAudit
from .events import CanonicalEventDB

__all__ = [
    "ConfigGlobal",
    "ConfigTenant",
    "ConfigDepartment",
    "ConfigGroup",
    "ConfigUser",
    "ConfigAudit",
    "CanonicalEventDB",
]