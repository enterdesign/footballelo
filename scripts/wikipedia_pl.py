"""Polish top flight (Liga 1927-39, I liga 1948-2008, Ekstraklasa 2008-) from English Wikipedia.

Every season article has its results as a `{{#invoke:sports results|main ...}}` cross table:

    |team1=KAT|team2=CZA ...          order of the teams
    |name_WIS=[[Wisła Kraków]]         code -> club (link target = one name per club over the years)
    |match_WIS_KAT=3–0                 home WIS, away KAT

Seasons with a split (championship / relegation round) have several such tables on the page;
all of them are read. Text is CC BY-SA (Wikipedia).
"""
import json
import re
import time
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/w/api.php"
RAW = "https://en.wikipedia.org/w/index.php?title={title}&action=raw"
UA = {"User-Agent": "footballelo/1.0 (https://github.com/enterdesign/footballelo; personal ELO project)"}
CATEGORY = "Category:Ekstraklasa seasons"
TITLE = re.compile(r"^(\d{4})(?:[–-](\d{2,4}))? Ekstraklasa$")
CALL_RE = re.compile(r"\{\{\s*#invoke:\s*sports results", re.I)
SCORE = re.compile(r"(\d+)\s*[–\-−]\s*(\d+)")


def http(url, retries=4):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(5 * (i + 1))


def season_titles():
    """{season label: article title} for all season articles in the category."""
    out, cont = {}, None
    while True:
        q = {"action": "query", "list": "categorymembers", "cmtitle": CATEGORY, "cmlimit": "500",
             "format": "json", "cmnamespace": "0"}
        if cont:
            q["cmcontinue"] = cont
        data = json.loads(http(API + "?" + urllib.parse.urlencode(q)))
        for m in data["query"]["categorymembers"]:
            label = season_label(m["title"])
            if label:
                out[label] = m["title"]
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            return dict(sorted(out.items()))


def season_label(title):
    m = TITLE.match(title)
    if not m:
        return None
    a, b = m.group(1), m.group(2)
    return f"{a}/{b[-2:]}" if b else a


def blocks(wikitext):
    """Bodies of all `{{#invoke:sports results|main ...}}` calls (nested templates respected)."""
    i = 0
    while True:
        m = CALL_RE.search(wikitext, i)               # module name case differs between articles
        if not m:
            return
        i = m.start()
        depth, j = 0, i
        while j < len(wikitext):
            if wikitext.startswith("{{", j):
                depth += 1
                j += 2
            elif wikitext.startswith("}}", j):
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        yield wikitext[m.end(): j - 2]
        i = j


def club(value):
    """`[[Pogoń Lwów (1904)|Pogoń Lwów]]` -> ("Pogoń Lwów", "Pogoń Lwów")  (link target, shown text)."""
    m = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", value)
    if not m:
        plain = re.sub(r"<[^>]+>|'''?", "", value).strip()
        return plain, plain
    target, shown = m.group(1).strip(), (m.group(2) or m.group(1)).strip()
    return re.sub(r"\s*\([^)]*\)$", "", target), shown


def params(body):
    """Top-level `|key=value` parameters (a `|` inside [[..]] or {{..}} does not split)."""
    out, depth, cur, i = [], 0, "", 0
    while i < len(body):
        two = body[i:i + 2]
        if two in ("[[", "{{"):
            depth += 1
            cur += two
            i += 2
        elif two in ("]]", "}}"):
            depth -= 1
            cur += two
            i += 2
        elif body[i] == "|" and depth == 0:
            out.append(cur)
            cur = ""
            i += 1
        else:
            cur += body[i]
            i += 1
    out.append(cur)
    return [p.strip() for p in out if "=" in p]


def parse_block(body):
    names, matches = {}, []
    for p in params(body):
        key, _, value = p.partition("=")
        key = key.strip()
        if key.startswith("name_"):
            names[key[5:]] = club(value)
        elif key.startswith("match_"):
            code = key[6:]
            home, _, away = code.partition("_")
            value = re.sub(r"(?s)<ref[^>]*/>|<ref.*?</ref>|<[^>]+>", "", value)
            s = SCORE.search(value)
            if s and away:
                matches.append((home, away, int(s.group(1)), int(s.group(2))))
    out = []
    for h, a, gh, ga in matches:
        if h in names and a in names:
            out.append({"teamA": names[h][0], "goalsA": gh, "teamB": names[a][0], "goalsB": ga,
                        "shownA": names[h][1], "shownB": names[a][1]})
    return out


def parse_season(wikitext, season):
    rows = []
    for b in blocks(wikitext):
        rows.extend(parse_block(b))
    return [{"season": season, "phase": "league", "teamA": r["teamA"], "goalsA": r["goalsA"],
             "teamB": r["teamB"], "goalsB": r["goalsB"]} for r in rows]


def fetch_season(title):
    return http(RAW.format(title=urllib.parse.quote(title.replace(" ", "_"))))
