from __future__ import annotations
import feedparser
import requests
from datetime import datetime, timezone
from typing import List, Optional
from .models import Article

# feedparser returns struct_time as entry.published_parsed/updated_parsed
def _parse_dt(entry):
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not t: return None
    return datetime(*t[:6], tzinfo=timezone.utc)

# Google News RSS links may redirect; resolve to canonical destination
def _resolve_final_url(url: str, timeout: float = 10.0) -> str:
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "news2x/0.1"})
        return r.url or url
    except Exception:
        return url

class GoogleNewsRSS:
    def __init__(self, lang: str, geo: str, ceid: str):
        self.lang = lang
        self.geo = geo
        self.ceid = ceid

    # Google News RSS search endpoint
    def fetch(self, query: str, max_items: int = 15) -> List[Article]:
        rss = ("https://news.google.com/rss/search?q=" + requests.utils.quote(query) + f"&hl={self.lang}&gl={self.geo}&ceid={self.ceid}")
        feed = feedparser.parse(rss)
        out = []
        for e in feed.entries[:max_items]:
            title = getattr(e, "title", "").strip()
            link = getattr(e, "link", "").strip()
            src = getattr(getattr(e, "source", None), "title", "") or "Google News"
            dt = _parse_dt(e)
            summary = getattr(e, "summary", "") or ""
            final = _resolve_final_url(link)
            out.append(Article(title=title, url=final, source=src, published_at=dt, summary=summary))
        return out