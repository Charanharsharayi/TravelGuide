import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Life Logistics Copilot"
    API_V1_STR: str = "/api"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Clerk
    CLERK_SECRET_KEY: str = os.getenv("CLERK_SECRET_KEY", "")
    _raw_key = os.getenv("CLERK_PEM_PUBLIC_KEY", "")
    # If the key was loaded but looks incomplete (just the header), it might be a parsing issue.
    # In this specific case, the user pasted it raw into .env.
    # We will try to reconstruct it if possible, but python-dotenv restricts what we can see.
    # A better approach for the USER is to fix the .env file.
    CLERK_PEM_PUBLIC_KEY: str = _raw_key
    
    # AI
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    OPENWEATHERMAP_API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")

settings = Settings()
