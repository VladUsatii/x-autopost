import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    # News
    query: str = os.getenv("NEWS_QUERY", "sports")
    rss_lang: str = os.getenv("NEWS_RSS_LANG", "en-US")
    rss_geo: str = os.getenv("NEWS_RSS_GEO", "US")
    rss_ceid: str = os.getenv("NEWS_RSS_CEID", "US:en")
    max_candidates: int = int(os.getenv("NEWS_MAX_CANDIDATES", "15"))

    # X OAuth2
    client_id: str = os.getenv("X_CLIENT_ID", "")
    client_secret: str = os.getenv("X_CLIENT_SECRET", "")
    redirect_uri: str = os.getenv("X_REDIRECT_URI", "http://127.0.0.1:8080/callback")

    # Token/state storage
    token_path: str = os.getenv("X_TOKEN_PATH", "./x_tokens.json")
    state_path: str = os.getenv("STATE_PATH", "./state.json")

    # Posting
    dry_run: bool = os.getenv("DRY_RUN", "0") == "1"
    include_link: bool = os.getenv("INCLUDE_LINK", "1") == "1"
    hashtag: str = os.getenv("HASHTAG", "#Sports")