from __future__ import annotations

from functools import lru_cache
from typing import Optional

from supabase import Client, create_client

from app.config import settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Optional[Client]:
    url = getattr(settings, "SUPABASE_URL", "") or ""
    service_role_key = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "") or ""

    if not url or not service_role_key:
        return None
    if url.startswith("<") or service_role_key.startswith("<"):
        return None

    return create_client(url, service_role_key)
