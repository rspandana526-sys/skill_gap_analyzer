import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GROQ_API_KEY    = os.environ.get("GROQ_API_KEY", "")
FAST2SMS_API_KEY = os.environ.get("FAST2SMS_API_KEY", "")
