"""
Configuration settings for OpenStudio application.
"""
import os
from typing import Optional
from dotenv import load_dotenv
import traceback

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        try:
            # OpenAI Configuration
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy-key")
            self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            
            # Groq Configuration
            self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            self.GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
            
            # Database Configuration
            self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./openstudio.db")
            self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            # Application Configuration
            self.HOST = os.getenv("HOST", "0.0.0.0")
            self.PORT = int(os.getenv("PORT", "8000"))
            self.DEBUG = os.getenv("DEBUG", "true").lower() in ('true', '1', 'yes', 'on')
            self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
            
            # Model Provider
            self.DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "openai")
        except Exception as e:
            print(f"❌ Error loading settings: {str(e)}")
            print("📋 Full traceback:")
            traceback.print_exc()
            # Set default values on error
            self.OPENAI_API_KEY = "dummy-key"
            self.OPENAI_MODEL = "gpt-4-turbo-preview"
            self.GROQ_API_KEY = None
            self.GROQ_MODEL = "mixtral-8x7b-32768"
            self.DATABASE_URL = "sqlite:///./openstudio.db"
            self.REDIS_URL = "redis://localhost:6379"
            self.HOST = "0.0.0.0"
            self.PORT = 8000
            self.DEBUG = True
            self.SECRET_KEY = "dev-secret-key"
            self.DEFAULT_MODEL_PROVIDER = "openai"


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Error creating settings instance: {str(e)}")
    print("📋 Full traceback:")
    traceback.print_exc()
    settings = None