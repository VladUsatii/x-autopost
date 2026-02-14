from __future__ import annotations
from dataclasses import replace
from .config import Config
from .state import load_state, save_state
from .news.google_rss import GoogleNewsRSS
from .news.select import select_best
from .news.extract import download_image, extract_og_image
from .rewrite.simple import rewrite_light
from .x.oauth2 import load_tokens, save_tokens, refresh_access_token
from .x.client import XClient
from .x.media import upload_image

def run_once(cfg: Config) -> dict:
    # Fetch candidates
    st = load_state(cfg.state_path)
    src = GoogleNewsRSS(cfg.rss_lang, cfg.rss_geo, cfg.rss_ceid)
    articles = src.fetch(cfg.query, max_items=cfg.max_candidates)

    chosen = select_best(articles, st.seen_urls, prefer_image=True)
    if not chosen: return {"status": "noop", "reason": "no_new_articles"}

    # Ensure image_url if possible
    if not chosen.image_url:
        img = extract_og_image(chosen.url)
        if img: chosen = replace(chosen, image_url=img)

    # Rewrite
    text = rewrite_light(chosen, hashtag=cfg.hashtag, include_link=cfg.include_link)

    if cfg.dry_run:
        st.seen_urls.add(chosen.url)
        save_state(cfg.state_path, st)
        return {"status": "dry_run", "text": text, "url": chosen.url, "image_url": chosen.image_url}

    # Auth: refresh token -> access token
    toks = load_tokens(cfg.token_path)
    if not toks.get("refresh_token"): raise RuntimeError(f"Missing refresh_token in {cfg.token_path}. Run: news2x auth")
    bundle = refresh_access_token(cfg.client_id, toks["refresh_token"], client_secret=cfg.client_secret)
    toks["access_token"] = bundle.access_token
    toks["refresh_token"] = bundle.refresh_token or toks["refresh_token"]
    save_tokens(cfg.token_path, toks)

    # Upload media
    media_ids = []
    if chosen.image_url:
        dl = download_image(chosen.image_url)
        if dl:
            img_bytes, mime = dl
            mid = upload_image(toks["access_token"], img_bytes, mime)
            media_ids = [mid]

    # Post and persist deduplication
    xc = XClient(toks["access_token"])
    resp = xc.create_post(text=text, media_ids=media_ids or None)
    st.seen_urls.add(chosen.url)
    save_state(cfg.state_path, st)
    return {"status": "posted", "response": resp, "chosen_url": chosen.url, "media_ids": media_ids}