import os
from dataclasses import dataclass


@dataclass
class ProviderSecrets:
    phaxio_api_key: str
    phaxio_api_secret: str
    phaxio_webhook_secret: str
    sinch_project_id: str
    sinch_api_key: str
    sinch_api_secret: str
    sinch_webhook_secret: str


def load_provider_secrets() -> ProviderSecrets:
    """Centralized secrets/env loader for provider credentials and webhook secrets.
    All modules should import from here instead of reading env directly.
    """
    return ProviderSecrets(
        phaxio_api_key=os.getenv("PHAXIO_API_KEY", ""),
        phaxio_api_secret=os.getenv("PHAXIO_API_SECRET", ""),
        phaxio_webhook_secret=os.getenv("PHAXIO_WEBHOOK_SECRET", os.getenv("PHAXIO_API_SECRET", "")),
        sinch_project_id=os.getenv("SINCH_PROJECT_ID", ""),
        sinch_api_key=os.getenv("SINCH_API_KEY", os.getenv("PHAXIO_API_KEY", "")),
        sinch_api_secret=os.getenv("SINCH_API_SECRET", os.getenv("PHAXIO_API_SECRET", "")),
        sinch_webhook_secret=os.getenv("SINCH_WEBHOOK_SECRET", ""),
    )

