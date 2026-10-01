"""Nations League results of the running edition from English Wikipedia (CC BY-SA).

The open results dataset lags behind by weeks, so the pages of the current edition
("2026–27 UEFA Nations League A/B/C/D" and the main article) are read as rendered HTML:
every match is a "footballbox" with date, the two teams and the score. Unplayed boxes are skipped.
"""
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import date

API = "https://en.wikipedia.org/w/api.php?action=parse&prop=text&format=json&formatversion=2&redirects=1&page="
BOX = re.compile(r'<div [^>]*class="footballbox"[^>]*>(.*?)(?=<div [^>]*class="footballbox"|<h[1-6][ >]|$)', re.S)
SCORE = re.compile(r"(\d+)\s*[–-]\s*(\d+)")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}")


def page_html(title):
    req = urllib.request.Request(API + urllib.parse.quote(title), headers={"User-Agent": "footballelo/1.0 (personal ELO project)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    return None if "error" in d else d["parse"]["text"]


def text(fragment):
    s = re.sub(r"<sup[^>]*>.*?</sup>|<style.*?</style>", "", fragment, flags=re.S)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def cell(block, cls):
    m = re.search(rf'<t[hd][^>]*class="[^"]*\b{cls}\b[^"]*"[^>]*>(.*?)</t[hd]>', block, re.S)
    return m.group(1) if m else ""


def parse_boxes(page):
    out = []
    for block in BOX.findall(page):
        day = DAY.search(block)
        score = SCORE.search(text(cell(block, "fscore")))
        if not day or not score:
            continue
        links = re.findall(r"<a [^>]*>([^<]+)</a>", cell(block, "fhome"))     # flag links hold only an image
        links2 = re.findall(r"<a [^>]*>([^<]+)</a>", cell(block, "faway"))
        a, b = (links[0] if links else text(cell(block, "fhome"))), (links2[0] if links2 else text(cell(block, "faway")))
        m = {"date": day.group(0), "teamA": html.unescape(a).strip(), "goalsA": int(score.group(1)),
             "teamB": html.unescape(b).strip(), "goalsB": int(score.group(2))}
        pen = re.search(r"Penalties.*?(\d+)\s*[–-]\s*(\d+)", text(block))
        if pen and m["goalsA"] == m["goalsB"] and pen.group(1) != pen.group(2):
            m["penWin"] = "A" if int(pen.group(1)) > int(pen.group(2)) else "B"
        out.append(m)
    return out


def titles(year):
    base = f"{year}–{str(year + 1)[2:]} UEFA Nations League"
    return [f"{base} {x}" for x in "ABCD"] + [base]


def fetch_running(today=None):
    """Matches played so far in the running edition (and the previous one before its finals ended)."""
    today = today or date.today()
    year = today.year if today.month >= 6 else today.year - 1
    out = []
    for y in (year - 1, year):
        for t in titles(y):
            try:
                page = page_html(t)
            except Exception:
                continue
            if page:
                out += parse_boxes(page)
    seen, uniq = set(), []
    for m in out:
        k = (m["date"], m["teamA"], m["teamB"])
        if k not in seen:
            seen.add(k)
            uniq.append(m)
    return uniq
