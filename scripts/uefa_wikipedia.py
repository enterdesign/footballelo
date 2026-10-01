"""Europa League (2009/10 →) and Conference League (2021/22 →) results from English Wikipedia (CC BY-SA).

Each season has a group-stage / league-phase article and a knockout-phase article. Every match is a
rendered "footballbox"; the stage comes from the nearest heading above it. Qualifying rounds are not
read (they are not rated). Teams are identified by the title of the article they link to, which is
stable across the display-name variants used from season to season.
"""
import html
import json
import re
import time
import urllib.parse
import urllib.request
from collections import Counter

import nl_wikipedia as nw

NAME = {"el": "UEFA Europa League", "conf": "UEFA Europa Conference League"}
FIRST = {"el": 2009, "conf": 2021}
TOKEN = re.compile(r'<h([2-4])[^>]*>(.*?)</h\1>|<div [^>]*class="footballbox"[^>]*>', re.S)
LINK = re.compile(r'<a [^>]*href="/wiki/([^"#?]+)[^"]*"[^>]*>([^<]+)</a>')
FLAG = re.compile(r"Flag_of_([^./\"]+)\.svg")


def label(year):
    return f"{year}/{str(year + 1)[2:]}"


def season_years(today):
    """Start years of the seasons that may still be changing: the running one (and the last one in summer)."""
    y = today.year if today.month >= 7 else today.year - 1
    return [y - 1, y] if today.month in (5, 6, 7, 8) else [y]


def titles(comp, year):
    """(league/group page, knockout page) for a season."""
    name = NAME[comp]
    if comp == "conf" and year >= 2024:
        name = "UEFA Conference League"
    base = f"{year}–{str(year + 1)[2:]} {name}"
    first = "league phase" if year >= 2024 else "group stage"
    return f"{base} {first}", f"{base} knockout phase"


def stage(head):
    h = head.lower()
    if "play-off" in h or "playoff" in h:
        return "po"
    if "round of 32" in h:
        return "r32"
    if "round of 16" in h:
        return "r16"
    if "quarter" in h:
        return "qf"
    if "semi" in h:
        return "sf"
    if h.strip() == "final":
        return "final"
    return None


def team(cell):
    """(article title, shown name, country) of a team cell."""
    links = [(urllib.parse.unquote(t).replace("_", " "), html.unescape(s).strip())
             for t, s in LINK.findall(cell) if not t.startswith(("File:", "Special:"))]
    flag = FLAG.search(cell)
    country = urllib.parse.unquote(flag.group(1)).replace("_", " ") if flag else ""
    if links:
        return links[0][0], links[0][1], country
    return nw.text(cell), nw.text(cell), country


def parse_page(page, season, phase=None):
    """Matches of one article. `phase` fixes the stage (group / league phase page); otherwise it comes from headings."""
    out, info = [], {}
    pos = [(m.start(), m) for m in TOKEN.finditer(page)]
    current = None                      # stage of the nearest heading that names one ("Summary", "Matches" do not)
    for i, (start, m) in enumerate(pos):
        if m.group(1):
            current = stage(re.sub(r"<[^>]+>", "", m.group(2)).strip()) or current
            continue
        end = pos[i + 1][0] if i + 1 < len(pos) else len(page)
        block = page[start:end]
        ph = phase or current
        day = nw.DAY.search(block)
        score = nw.SCORE.search(nw.text(nw.cell(block, "fscore")))
        if not ph or not day or not score:
            continue
        a, b = team(nw.cell(block, "fhome")), team(nw.cell(block, "faway"))
        rec = {"season": season, "phase": ph, "teamA": a[0], "goalsA": int(score.group(1)),
               "teamB": b[0], "goalsB": int(score.group(2))}
        if re.search(r"a\.e\.t", nw.text(nw.cell(block, "fscore"))):
            rec["et"] = True
        pen = re.search(r"Penalties.*?(\d+)\s*[–-]\s*(\d+)", nw.text(block))
        if pen and rec["goalsA"] == rec["goalsB"]:
            rec["penA"], rec["penB"] = int(pen.group(1)), int(pen.group(2))
        rec["date"] = day.group(0)
        out.append(rec)
        for t, shown, country in (a, b):
            d = info.setdefault(t, {"shown": Counter(), "country": Counter()})
            d["shown"][shown] += 1
            if country:
                d["country"][country] += 1
    return out, info


def fetch_season(comp, year):
    """(matches, info) of one season; missing articles give nothing."""
    first_t, ko_t = titles(comp, year)
    matches, info = [], {}
    for t, ph in ((first_t, "group"), (ko_t, None)):
        try:
            page = nw.page_html(t)
        except Exception as e:
            print(f"  Wikipedia page '{t}' failed: {e}")
            continue
        if not page:
            continue
        ms, inf = parse_page(page, label(year), ph)
        matches += ms
        for k, v in inf.items():
            d = info.setdefault(k, {"shown": Counter(), "country": Counter()})
            d["shown"].update(v["shown"])
            d["country"].update(v["country"])
    return matches, info


def resolve_redirects(titles_, delay=0.6):
    """{title -> final article title} for redirects (a club is often linked by an old name)."""
    out = {}
    titles_ = sorted(titles_)
    for i in range(0, len(titles_), 50):
        chunk = titles_[i:i + 50]
        url = ("https://en.wikipedia.org/w/api.php?action=query&format=json&formatversion=2&redirects=1&titles="
               + urllib.parse.quote("|".join(chunk)))
        for attempt in range(5):
            time.sleep(delay)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "footballelo/1.0 (personal ELO project)"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    d = json.load(r)["query"]
                break
            except Exception:
                time.sleep(8 * (attempt + 1))
        else:
            continue
        norm = {n["from"]: n["to"] for n in d.get("normalized", [])}
        red = {r["from"]: r["to"] for r in d.get("redirects", [])}
        for t in chunk:
            n = norm.get(t, t)
            out[t] = red.get(n, n)
    return out
