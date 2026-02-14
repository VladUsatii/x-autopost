from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from typing import Optional

def extract_og_image(url: str, timeout: float = 10.0):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "news2x/0.1"})
        if r.status_code >= 400: return None
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
        if not tag: return None
        content = tag.get("content")
        if not content: return None
        return content.strip()
    except Exception: return None

# Returns (bytes, mime) or None. max_bytes is a safety cap
def download_image(url: str, max_bytes=6_000_000, timeout=15.0):
    try:
        r = requests.get(url, timeout=timeout, stream=True, headers={"User-Agent": "news2x/0.1"})
        if r.status_code >= 400: return None
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower() or "application/octet-stream"
        buf = bytearray()
        for chunk in r.iter_content(chunk_size=64 * 1024):
            if not chunk: continue
            buf.extend(chunk)
            if len(buf) > max_bytes: return None
        return (bytes(buf), ctype)
    except Exception: return None