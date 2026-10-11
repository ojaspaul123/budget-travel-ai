from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "AIzaSyCaAcQnBSrOistuuBXIl_AU5i3lVMxvklk")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()

if __name__ == "__main__":
    print("Google Maps Key loaded:", bool(settings.GOOGLE_MAPS_API_KEY))
    print("Gemini Key loaded:", bool(settings.GEMINI_API_KEY))