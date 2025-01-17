from supabase import create_client, Client
from functools import lru_cache
import os

@lru_cache()
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_API_URL")
    key = os.getenv("SUPABASE_API_KEY")
    return create_client(url, key)