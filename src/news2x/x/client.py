from __future__ import annotations
import requests

API_BASE = "https://api.x.com"

class XClient:
    def __init__(self, user_access_token: str):
        self.tok = user_access_token

    def _headers_json(self): return { "Authorization": f"Bearer {self.tok}", "Content-Type": "application/json" }

    # POST /2/tweets with Bearer user token
    def create_post(self, text: str, media_ids=None):
        payload: dict = {"text": text}
        if media_ids: payload["media"] = {"media_ids": media_ids}
        r = requests.post(f"{API_BASE}/2/tweets", json=payload, headers=self._headers_json(), timeout=15)
        r.raise_for_status()
        return r.json()