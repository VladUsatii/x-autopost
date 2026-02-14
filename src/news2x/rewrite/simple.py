from __future__ import annotations
import re
from ..news.models import Article

def rewrite_light(article: Article, hashtag: str = "#Sports", include_link: bool = True) -> str:
    """
    Deterministic, “light” rewrite:
      - Strip noisy suffixes (e.g., " - ESPN")
      - Normalize whitespace
      - Add a lead-in
      - Enforce 280-char budget by truncation (keeps link if present)
    """
    title = article.title.strip()
    title = re.sub(r"\s+[-|–]\s+[A-Za-z0-9 .]{2,}$", "", title).strip()  # naive suffix chop
    title = re.sub(r"\s+", " ", title)
    lead = "UPDATE:"
    link = f" {article.url}" if (include_link and article.url) else ""
    tag = f" {hashtag}".strip()
    text = f"{lead} {title}.{link} {tag}".strip()

    # preserve end tag/link if possible
    if len(text) > 280:
        tail = (link + " " + tag).strip()
        budget = 280 - (len(tail) + 1)
        head = (f"{lead} {title}.").strip()
        head = head[: max(0, budget)].rstrip()
        text = (head + " " + tail).strip()
        text = text[:280]
    return text