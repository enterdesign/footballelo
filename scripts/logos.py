#!/usr/bin/env python3
"""Fill the missing "logo" field of clubs in data/teams_ucl.json and teams_pl.json from TheSportsDB.

Existing "logo" values are never touched, so a wrong logo can be fixed by hand
(put any image URL in the "logo" field). Clubs that cannot be matched
unambiguously are listed at the end; add their "logo" manually.

usage: logos.py [--key KEY]     (default key "3" is TheSportsDB's public test key)
"""
import argparse
import json
import time
import unicodedata
import urllib.parse
import urllib.request

from common import DATA

API = "https://www.thesportsdb.com/api/v1/json/{key}/searchteams.php?t={q}"


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return "".join(c for c in s if c.isalnum())


def search(key, q):
    url = API.format(key=key, q=urllib.parse.quote(q))
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return [t for t in (json.load(r).get("teams") or []) if t.get("strSport") == "Soccer"]
        except Exception:
            time.sleep(5 * (attempt + 1))
    return []


WIKI = ("https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrlimit=3&prop=pageimages"
        "&piprop=original&format=json&gsrsearch={q}")


def wiki_logo(name):
    """Fallback: lead image (the crest) of the Wikipedia article found for "<name> football club"."""
    url = WIKI.format(q=urllib.parse.quote(f"{name} football club"))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "footballelo/1.0 (personal ELO project)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            pages = sorted((json.load(r).get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 9))
    except Exception:
        return None
    words = [w for w in (norm(t) for t in name.split()) if len(w) >= 3]
    for p in pages:
        src = (p.get("original") or {}).get("source")
        if src and any(w in norm(p["title"]) for w in words) and src.lower().endswith((".png", ".svg", ".jpg", ".jpeg")):
            return src
    return None


def pick(results, country):
    same = [t for t in results if norm(t.get("strCountry") or "")[:5] == norm(country)[:5]]
    if same:
        return same[0]
    return results[0] if len(results) == 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default="3")
    args = ap.parse_args()
    for fname in ("teams_ucl.json", "teams_pl.json", "teams_ekstraklasa.json"):
        path = DATA / fname
        teams = json.loads(path.read_text(encoding="utf-8"))
        missing = []
        for name, info in teams.items():
            if info.get("logo"):
                continue
            hit = None
            for q in [name, *info.get("aliases", [])][:3]:
                hit = pick(search(args.key, q), info.get("country", ""))
                time.sleep(2.2)                  # free tier: ~30 requests / minute
                if hit:
                    break
            badge = (hit or {}).get("strBadge") or (hit or {}).get("strTeamBadge")
            if not badge:
                badge = wiki_logo(name)
                time.sleep(1)
            if badge:
                info["logo"] = badge
            else:
                missing.append(name)
        path.write_text(json.dumps(teams, ensure_ascii=False, indent=1), encoding="utf-8")
        found = sum(1 for t in teams.values() if t.get("logo"))
        print(f"{fname}: logos {found}/{len(teams)}")
        if missing:
            print("  no logo found for:", ", ".join(missing))


if __name__ == "__main__":
    main()
