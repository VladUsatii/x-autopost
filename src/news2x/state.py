import json, os, time
from dataclasses import dataclass
from typing import Set

@dataclass
class State:
    seen_urls: Set[str]

def load_state(path: str) -> State:
    if not os.path.exists(path): return State(seen_urls=set())
    with open(path, "r", encoding="utf-8") as f: obj = json.load(f)
    return State(seen_urls=set(obj.get("seen_urls", [])))

def save_state(path: str, st: State):
    tmp = { "seen_urls": sorted(st.seen_urls), "updated_at_unix": int(time.time()) }
    with open(path, "w", encoding="utf-8") as f: json.dump(tmp, f, indent=2)