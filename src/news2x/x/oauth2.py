from __future__ import annotations
import base64, json, os, secrets, string, urllib.parse, requests
from dataclasses import dataclass
from typing import Optional

AUTH_URL = "https://x.com/i/oauth2/authorize"
TOKEN_URL = "https://api.x.com/2/oauth2/token"
DEFAULT_SCOPES = ["tweet.write", "users.read", "offline.access", "media.write"]

def _rand_verifier(n: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits + "-._~"
    return "".join(secrets.choice(alphabet) for _ in range(n))

@dataclass
class TokenBundle:
    access_token: str
    refresh_token: Optional[str]
    token_type: str = "bearer"

# Returns (url, state, code_verifier). Uses code_challenge_method=plain for maximal compatibility
def build_authorize_url(client_id: str, redirect_uri: str, scopes=DEFAULT_SCOPES):
    state = secrets.token_urlsafe(24)
    code_verifier = _rand_verifier()
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params), state, code_verifier

def exchange_code_for_token(client_id: str, redirect_uri: str, code: str, code_verifier: str, client_secret: str = "") -> TokenBundle:
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if client_secret:
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {basic}"

    r = requests.post(TOKEN_URL, data=data, headers=headers, timeout=15)
    r.raise_for_status()
    obj = r.json()
    return TokenBundle(
        access_token=obj["access_token"],
        refresh_token=obj.get("refresh_token"),
        token_type=obj.get("token_type", "bearer"),
    )

def refresh_access_token(client_id: str, refresh_token: str, client_secret: str = "") -> TokenBundle:
    data = { "grant_type": "refresh_token", "client_id": client_id, "refresh_token": refresh_token }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if client_secret:
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("ascii")
        headers["Authorization"] = f"Basic {basic}"

    r = requests.post(TOKEN_URL, data=data, headers=headers, timeout=15)
    r.raise_for_status()
    obj = r.json()
    return TokenBundle( access_token=obj["access_token"], refresh_token=obj.get("refresh_token", refresh_token), token_type=obj.get("token_type", "bearer") )

def load_tokens(path: str):
    if not os.path.exists(path): return {}
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def save_tokens(path: str, obj: dict):
    with open(path, "w", encoding="utf-8") as f: json.dump(obj, f, indent=2)