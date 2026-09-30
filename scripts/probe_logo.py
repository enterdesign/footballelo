#!/usr/bin/env python3
"""One-off: trace the Wikipedia crest lookup step by step."""
import re
import traceback

import logos

for name in ("Nottingham Forest", "Hamburger SV", "Podbeskidzie Bielsko-Biała"):
    print("=====", name)
    try:
        words = [w for w in (logos.norm(t) for t in name.split()) if len(w) >= 3]
        hits = logos.wiki(action="query", list="search", srsearch=f"{name} football club", srlimit=3)["query"]["search"]
        print("hits:", [h["title"] for h in hits], "words:", words)
        title = next((h["title"] for h in hits if any(w in logos.norm(h["title"]) for w in words)
                      and not re.search(r"season|stadium", h["title"], re.I)), None)
        print("title:", title)
        pages = logos.wiki(action="query", titles=title, prop="images", imlimit=60)["query"]["pages"]
        files = [i["title"] for p in pages.values() for i in p.get("images", [])]
        print("files:", files[:25])
        good = [f for f in files if logos.CREST.search(f) and not logos.NOT_CREST.search(f)
                and f.lower().endswith((".svg", ".png"))]
        print("good:", good)
        if good:
            info = logos.wiki(action="query", titles=good[0], prop="imageinfo", iiprop="url")["query"]["pages"]
            print("info:", info)
    except Exception:
        traceback.print_exc()
