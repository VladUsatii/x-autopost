from __future__ import annotations
import requests

# Simple image upload via POST /2/media/upload using multipart form-data
def upload_image(user_access_token: str, img_bytes: bytes, mime: str) -> str:
    headers = {"Authorization": f"Bearer {user_access_token}"}
    files = {"media": ("image", img_bytes, mime)}
    data = { "media_category": "tweet_image", "media_type": mime, "shared": "false" }
    r = requests.post(f"https://api.x.com/2/media/upload", headers=headers, files=files, data=data, timeout=30)
    r.raise_for_status()
    obj = r.json()
    return obj["data"]["id"]