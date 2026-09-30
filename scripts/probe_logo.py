#!/usr/bin/env python3
"""One-off: why does the Wikipedia logo fallback find nothing?"""
import json
import urllib.parse
import urllib.request

import logos

for name in ("Nottingham Forest", "Hamburger SV", "Zenit St. Petersburg", "Podbeskidzie Bielsko-Biała",
             "Polonia Bytom", "Dyskobolia Grodzisk Wielkopolski"):
    url = logos.WIKI.format(q=urllib.parse.quote(f"{name} football club"))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "footballelo/1.0 (personal ELO project)"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        pages = (data.get("query") or {}).get("pages", {})
        print(name, "->", [(p.get("index"), p.get("title"), (p.get("original") or {}).get("source")) for p in pages.values()])
    except Exception as e:
        print(name, "ERROR", repr(e))
    print("   wiki_logo:", logos.wiki_logo(name))
