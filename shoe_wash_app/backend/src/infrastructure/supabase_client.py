import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]


def get_client() -> Client:
    """Create a Supabase client. This is the only file that knows Supabase exists."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)