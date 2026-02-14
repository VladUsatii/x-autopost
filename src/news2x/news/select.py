from __future__ import annotations
from dataclasses import replace
from typing import Iterable, Optional
from .models import Article
from .extract import extract_og_image

# Keep provider ordering. Skip URLs already seen. Prefer first item with an extractable og:image if prefer_image=True
def select_best(articles: Iterable[Article], seen_urls: set[str], prefer_image: bool = True):
    fresh = [a for a in articles if a.url and a.url not in seen_urls]
    if not fresh: return None
    if not prefer_image: return fresh[0]
    for a in fresh:
        img = extract_og_image(a.url)
        if img: return replace(a, image_url=img)
    return fresh[0]