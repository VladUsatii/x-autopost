from __future__ import annotations
import argparse
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

from .config import Config
from .job import run_once
from .x.oauth2 import ( build_authorize_url, exchange_code_for_token, load_tokens, save_tokens )

# Store result on server instance
class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        self.server.auth_code = qs.get("code", [None])[0]
        self.server.state = qs.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK. You can close this tab.")
    def log_message(self, fmt, *args): return

def cmd_auth(cfg: Config) -> int:
    if not cfg.client_id:
        print("ERROR: set X_CLIENT_ID", file=sys.stderr)
        return 2

    url, state, verifier = build_authorize_url(cfg.client_id, cfg.redirect_uri)
    toks = load_tokens(cfg.token_path)
    toks["pkce_state"] = state
    toks["pkce_verifier"] = verifier
    save_tokens(cfg.token_path, toks)

    print("Open this URL in a browser and authorize:")
    print(url)
    print("\nWaiting for callback on redirect_uri (must match your app settings)...")

    # Start local callback server matching redirect_uri host/port/path
    u = urllib.parse.urlparse(cfg.redirect_uri)
    host = u.hostname or "127.0.0.1"
    port = u.port or 8080

    httpd = HTTPServer((host, port), _CallbackHandler)
    httpd.auth_code = None
    httpd.state = None

    while httpd.auth_code is None: httpd.handle_request()

    if httpd.state != state:
        print("ERROR: state mismatch", file=sys.stderr)
        return 3

    code = httpd.auth_code
    bundle = exchange_code_for_token( client_id=cfg.client_id, redirect_uri=cfg.redirect_uri, code=code, code_verifier=verifier, client_secret=cfg.client_secret )
    toks = load_tokens(cfg.token_path)
    toks["access_token"] = bundle.access_token
    toks["refresh_token"] = bundle.refresh_token
    save_tokens(cfg.token_path, toks)
    print("Saved tokens to", cfg.token_path)
    return 0

def cmd_run(cfg: Config):
    out = run_once(cfg)
    print(out)
    return 0 if out.get("status") in ("posted", "dry_run", "noop") else 1

def main():
    ap = argparse.ArgumentParser(prog="news2x")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth", help="One-time OAuth2 setup; saves refresh token")
    sub.add_parser("run", help="Run once (use cron to schedule)")
    args = ap.parse_args()
    cfg = Config()
    if args.cmd == "auth": raise SystemExit(cmd_auth(cfg))
    if args.cmd == "run": raise SystemExit(cmd_run(cfg))