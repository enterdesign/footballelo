#!/usr/bin/env python3
"""One-off: look at the wikitext of seasons the importer could not fully read."""
import re

import wikipedia_pl as wp

titles = wp.season_titles()
for label in ("2010/11", "2007/08", "2013/14"):
    wt = wp.fetch_season(titles[label])
    print("=====", label, len(wt), "invoke:", wt.count("{{#invoke:"), "football results:", wt.lower().count("football results"),
          "wikitables:", wt.count("wikitable"))
    for m in re.finditer(r"\{\{[#A-Za-z ]*(?:results|Results)[^|}\n]*", wt):
        print("  template:", m.group(0)[:80])
        break
    i = wt.find("==Results")
    print(wt[i:i + 1600] if i >= 0 else "(no ==Results)")
for label in ("2001/02", "1952", "1962", "1933", "1986/87", "1992/93"):
    wt = wp.fetch_season(titles[label])
    print("=====", label, "blocks:")
    for k, b in enumerate(wp.blocks(wt)):
        ms = wp.parse_block(b)
        teams = {t for m in ms for t in (m["teamA"], m["teamB"])}
        print(f"  block {k}: {len(ms)} matches, {len(teams)} teams; header: {b[:110]!r}")
