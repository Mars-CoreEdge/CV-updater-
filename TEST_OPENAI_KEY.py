import os
import sys
import requests

# Try to load .env from backend directory
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print(f"Loaded environment from {dotenv_path}")
    else:
        print(f"No .env file found at {dotenv_path}, continuing...")
except ImportError:
    print("[INFO] python-dotenv not installed. To auto-load .env, run: pip install python-dotenv")

API_KEY = os.getenv("VITE_OPENAI_API_KEY")

print("--- OpenAI API Key Test ---")

if not API_KEY:
    print("❌ VITE_OPENAI_API_KEY environment variable not set.")
    print("💡 Set it in backend/.env or export it in your shell.")
    sys.exit(1)

if not API_KEY.startswith("sk-") or len(API_KEY) < 20:
    print("❌ VITE_OPENAI_API_KEY format is invalid (should start with 'sk-' and be at least 20 chars)")
    sys.exit(1)

print(f"✅ VITE_OPENAI_API_KEY found: {API_KEY[:10]}...{API_KEY[-4:]}")

# Optional: Make a real API call to OpenAI (list models)
try:
    response = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=10
    )
    if response.status_code == 200:
        print("✅ OpenAI API key is valid! (Successfully listed models)")
    elif response.status_code == 401:
        print("❌ OpenAI API key is invalid or unauthorized (401)")
    else:
        print(f"⚠️ Unexpected response from OpenAI: {response.status_code} {response.text}")
except Exception as e:
    print(f"❌ Error connecting to OpenAI API: {e}") 