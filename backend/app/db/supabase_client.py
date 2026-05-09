from supabase import create_client, Client
from app.config import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


async def ping_supabase():
    """Test Supabase connection on startup."""
    try:
        result = supabase.table("complaints").select("complaint_id").limit(1).execute()
        print("[Supabase] Connected successfully to JANSETU database")
        return True
    except Exception as e:
        print(f"[Supabase] Connection failed: {e}")
        return False
