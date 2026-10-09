from app.integrations.crm.base import CRMProvider
from app.integrations.crm.local import LocalCRMProvider

_local_provider: LocalCRMProvider | None = None


def get_crm_provider() -> CRMProvider:
    global _local_provider
    if _local_provider is None:
        _local_provider = LocalCRMProvider()
    return _local_provider
