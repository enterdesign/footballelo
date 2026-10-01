"""UEFA Nations League: import from the open `international_results` dataset and turn the raw
matches into rated ones (edition, division phase).

The dataset has no divisions and no stage names, so both are derived:
* the groups of an edition are the connected sets of teams that play each other in the league phase;
* the first edition's divisions are listed in data/nl_leagues.json; later editions are inferred from the
  previous one (a group's division = the average previous division of its teams, using the number of
  groups per division given in the file, or copied from the previous edition for a brand new edition);
* knockout matches: A-division matches after the league phase are quarter-finals, except the last four
  of an edition (semi-finals, 3rd place, final); matches between two divisions are play-offs.
"""
import csv
import io
import urllib.request
from datetime import date

RESULTS = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
SHOOTOUTS = "https://raw.githubusercontent.com/martj42/international_results/master/shootouts.csv"
TOURNAMENT = "UEFA Nations League"
DIVISIONS = "ABCD"
LEAGUE_GAP = 110        # days: a longer pause after the start of an edition ends its league phase
MAX_EDITION_DAYS = 800


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "footballelo/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def parse(results_csv, shootouts_csv, tournament=TOURNAMENT):
    """Raw matches of one tournament in date order; a shoot-out winner is stored as "penWin": "A" | "B"."""
    won = {(r["date"], r["home_team"], r["away_team"]): r["winner"] for r in csv.DictReader(io.StringIO(shootouts_csv))}
    out = []
    for r in csv.DictReader(io.StringIO(results_csv)):
        if r["tournament"] != tournament or r["home_score"] in ("", "NA"):
            continue
        m = {"date": r["date"], "teamA": r["home_team"], "goalsA": int(r["home_score"]),
             "teamB": r["away_team"], "goalsB": int(r["away_score"])}
        w = won.get((r["date"], r["home_team"], r["away_team"]))
        if w:
            m["penWin"] = "A" if w == r["home_team"] else "B"
        out.append(m)
    out.sort(key=lambda m: m["date"])
    return out


def days(a, b):
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def label(d):
    y = int(d[:4])
    return f"{y}/{str(y + 1)[2:]}"


def split_editions(matches, editions):
    """[(label, [matches])]. Declared editions have "from"/"to"; later matches form new editions."""
    out = [(lab, []) for lab in editions]
    bounds = [(e["from"], e["to"]) for e in editions.values()]
    extra = None
    for m in matches:
        for (lab, bucket), (lo, hi) in zip(out, bounds):
            if lo <= m["date"] <= hi:
                bucket.append(m)
                break
        else:
            if m["date"] < bounds[0][0]:
                raise ValueError(f"Nations League match {m['date']} is before the first edition")
            if extra is None or days(extra[1][0]["date"], m["date"]) > MAX_EDITION_DAYS:
                extra = (label(m["date"]), [])
                out.append(extra)
            extra[1].append(m)
    return out


def groups_of(league):
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for m in league:
        parent[find(m["teamA"])] = find(m["teamB"])
    comps = {}
    for t in list(parent):
        comps.setdefault(find(t), set()).add(t)
    return sorted(comps.values(), key=lambda s: sorted(s)[0])


def league_phase(ms):
    """Matches up to the first long pause."""
    for i in range(1, len(ms)):
        if days(ms[i - 1]["date"], ms[i]["date"]) > LEAGUE_GAP:
            return ms[:i], ms[i:]
    return ms, []


def infer_divisions(groups, prev, counts):
    """{team: division} for the groups of an edition, given the previous edition's {team: division}.
    Complete edition: the groups with the lowest average previous division get A, then B ... in the
    numbers given by `counts`. While the league phase is still being played the groups are incomplete
    (pairs, triples), so each one is simply rounded to the nearest division (everything is rebuilt
    from scratch on every run, so the final build uses the complete groups)."""
    def level(g):
        return sum(DIVISIONS.index(prev[t]) if t in prev else 3.5 for t in g) / len(g)
    out = {}
    if len(groups) == sum(counts.values()):
        order, i = sorted(groups, key=lambda g: (level(g), sorted(g)[0])), 0
        for d in DIVISIONS:
            for g in order[i:i + counts[d]]:
                out.update({t: d for t in g})
            i += counts[d]
    else:
        for g in groups:
            out.update({t: DIVISIONS[min(3, int(level(g) + 0.49))] for t in g})
    return out


def prepare(raw, cfg, canon=lambda t: t):
    """Raw matches -> rated matches with "season" and "phase".
    `canon` maps source names to canonical ones (sources spell some teams differently).
    Returns (matches, latest) where latest = {team: division in its most recent edition}."""
    raw = [{**m, "teamA": canon(m["teamA"]), "teamB": canon(m["teamB"])} for m in raw]
    editions = {lab: {**e, **({"divisions": {d: [canon(t) for t in ts] for d, ts in e["divisions"].items()}} if e.get("divisions") else {})}
                for lab, e in cfg["editions"].items()}
    out, latest, prev, counts = [], {}, None, None
    for lab, ms in split_editions(raw, editions):
        spec = editions.get(lab, {})
        league, ko = league_phase(ms)
        groups = groups_of(league)
        if spec.get("divisions"):
            div = {t: d for d, ts in spec["divisions"].items() for t in ts}
            missing = {t for g in groups for t in g} - set(div)
            if missing:
                raise ValueError(f"{lab}: teams without a division: {sorted(missing)}")
        else:
            div = infer_divisions(groups, prev, spec.get("groups") or counts)
        counts = {d: len({frozenset(g) for g in groups if div[next(iter(g))] == d}) for d in DIVISIONS}
        prev = div
        latest.update(div)
        for m in league:
            out.append({**m, "season": lab, "phase": div[m["teamA"]]})
        top = [m for m in ko if div[m["teamA"]] == div[m["teamB"]] == "A"]
        finals = top[-4:] if len(top) >= 4 else []
        names = {}
        if finals:
            sf = finals[:2]
            winners = {winner(m) for m in sf}
            for m in finals[:2]:
                names[id(m)] = "sf"
            for m in finals[2:]:
                names[id(m)] = "final" if {m["teamA"], m["teamB"]} == winners else "3rd"
        for m in ko:
            if id(m) in names:
                phase = names[id(m)]
            else:
                a, b = sorted((DIVISIONS.index(div[m["teamA"]]), DIVISIONS.index(div[m["teamB"]])))
                if a == b:
                    phase = "qf" if a == 0 else DIVISIONS[a]
                else:
                    phase = f"po{DIVISIONS[a]}{DIVISIONS[b]}" if b - a == 1 else DIVISIONS[b]
            out.append({**m, "season": lab, "phase": phase})
    return out, latest


def winner(m):
    if m.get("penWin"):
        return m["teamA"] if m["penWin"] == "A" else m["teamB"]
    return m["teamA"] if m["goalsA"] > m["goalsB"] else m["teamB"]
