"""Main application entry point for OpenStudio."""

import uvicorn
import traceback
import sys
from api.endpoints import app
from config import settings

if __name__ == "__main__":
    try:
        print("🎬 Starting OpenStudio Multi-Agent Storytelling Platform...")
        print(f"🌐 Server will be available at: http://{settings.HOST}:{settings.PORT}")
        print(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
        print(f"🔧 Debug mode: {settings.DEBUG}")
        
        uvicorn.run(
            "api.endpoints:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info" if not settings.DEBUG else "debug"
        )
    except Exception as e:
        print(f"❌ Error starting OpenStudio server: {str(e)}")
        print("📋 Full traceback:")
        traceback.print_exc()
        sys.exit(1)