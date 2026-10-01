#!/usr/bin/env python3
"""Fill the missing "logo" field of clubs in data/teams_ucl.json and teams_pl.json from TheSportsDB.

Existing "logo" values are never touched, so a wrong logo can be fixed by hand
(put any image URL in the "logo" field). Clubs that cannot be matched
unambiguously are listed at the end; add their "logo" manually.

usage: logos.py [--key KEY]     (default key "3" is TheSportsDB's public test key)
"""
import argparse
import json
import re
import time
import unicodedata
import urllib.error
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


WIKI_API = "https://en.wikipedia.org/w/api.php?format=json&"
CREST = re.compile(r"(logo|crest|badge|emblem|coat[ _]of|shield)", re.I)
NOT_CREST = re.compile(r"(flag[ _]of|commons-logo|wikiproject|wikimedia|wiktionary|ambox|question|icon|kit|stadium)", re.I)


def wiki(**params):
    """Wikipedia API call: spaced out and retried, because bursts get rate limited."""
    url = WIKI_API + urllib.parse.urlencode(params)
    for attempt in range(5):
        time.sleep(0.6)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "footballelo/1.0 (personal ELO project)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise
            time.sleep(8 * (attempt + 1))


def wiki_logo(name):
    """Fallback: the crest file listed on the Wikipedia article of "<name> football club".
    (Most crests are non-free files, which the lead-image API hides, so the file list is read.)"""
    words = [w for w in (norm(t) for t in name.split()) if len(w) >= 3]
    try:
        hits = wiki(action="query", list="search", srsearch=f"{name} football club", srlimit=3)["query"]["search"]
        title = next((h["title"] for h in hits if any(w in norm(h["title"]) for w in words)
                      and not re.search(r"season|stadium", h["title"], re.I)), None)
        if not title:
            return None
        pages = wiki(action="query", titles=title, prop="images", imlimit=500)["query"]["pages"]
        files = [i["title"] for p in pages.values() for i in p.get("images", [])]
        good = [f for f in files if CREST.search(f) and not NOT_CREST.search(f) and f.lower().endswith((".svg", ".png"))]
        if not good:
            return None
        info = wiki(action="query", titles=good[0], prop="imageinfo", iiprop="url")["query"]["pages"]
        url = next(iter(info.values())).get("imageinfo", [{}])[0].get("url")
        return url.split("?")[0] if url else None
    except Exception:
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
    for fname in ("teams_ucl.json", "teams_pl.json", "teams_ekstraklasa.json", "teams_el.json", "teams_conf.json"):
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
