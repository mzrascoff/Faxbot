"""Environment to DB config importer (stub).

This utility imports selected environment variable prefixes into the
hierarchical configuration store. In this repo skeleton, we provide a
no-op implementation that can be wired to the Phase 3 provider later.
"""
from __future__ import annotations

from typing import Iterable
import os


def import_env_to_db(prefixes: Iterable[str]) -> int:
    """Import env keys with given prefixes into DB config (stub).

    Returns the number of keys discovered. In a full implementation,
    this would write decrypted values into the hierarchical config,
    redacting secrets in audit logs. Here we simply count keys.
    """
    count = 0
    pref = tuple(p.upper() for p in prefixes)
    for k, _ in os.environ.items():
        if k.upper().startswith(pref):
            count += 1
    return count

