import random
import requests
from config import FAST2SMS_API_KEY


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_sms(phone, otp):
    """Send OTP via SMS using Fast2SMS (free Indian SMS API)."""
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            "variables_values": otp,
            "route": "otp",
            "numbers": phone,
        }
        headers = {
            "authorization": FAST2SMS_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()
        if data.get("return") is True:
            return True
        else:
            print(f"Fast2SMS error: {data}")
            return False
    except Exception as e:
        print(f"SMS error: {e}")
        return False
