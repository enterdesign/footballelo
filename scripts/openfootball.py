"""Parsers for openfootball plain-text fixtures (World Cup and Champions League).

Every parser yields dicts:
  {phase, teamA, goalsA, teamB, goalsB, [penA, penB], [et], [codeA, codeB]}
Goals are the score after extra time (if played). penA/penB are shoot-out goals.
"""
import re
from pathlib import Path

SCORE = re.compile(r"(?<![\d:])(\d+)-(\d+)(?![\d:])")
PEN = re.compile(r",?\s*(\d+)-(\d+)\s*pen\.?")
PEN_FIRST = re.compile(r"(\d+)-(\d+)\s*pen\.?\s*(\d+)-(\d+)\s*a\.e\.t\.?")
PREFIX = re.compile(
    r"^\s*(?:\(\d+\)\s*)?"                       # (73)
    r"(?:\d{1,2}:\d{2}(?:\s+UTC[+-]\d+)?\s+)?"   # 18:00 UTC-4
    r"(?:\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"|[A-Z][a-z]{2}\s+[A-Z][a-z]{2,8}\s+\d{1,2}\s{2,})?"  # 16 June / Sat Dec 3
)
CC = re.compile(r"\s*\(([A-Z]{3})\)\s*$")

WC_PHASES = [
    (r"group|matchday|play-?off|first round|second round|final round|round-robin", "group"),
]


def wc_phase(h):
    h = h.lower()
    if "third" in h or "3rd" in h:
        return "3rd"
    if "round of 32" in h:
        return "r32"
    if "round of 16" in h:
        return "r16"
    if "quarter" in h:
        return "qf"
    if "semi" in h:
        return "sf"
    if h.strip() in ("final", "finals"):
        return "final"
    if re.search(r"group|gruppe|matchday|round|play-?off", h):
        return "group"
    return None


def parse_wc_match(line):
    """Return match dict or None for a World Cup fixture line."""
    if "@" in line:
        body = line.split("@", 1)[0]
    else:
        body = line
    m = SCORE.search(body)
    if not m or line.lstrip().startswith(("#", "(", "▪")) and not re.match(r"\s*\(\d+\)", line):
        return None
    body = PREFIX.sub("", body, count=1)
    m = SCORE.search(body)
    if not m:
        return None
    pf = PEN_FIRST.match(body[m.start():])
    if pf:                                 # "0-3 pen. 0-0 a.e.t."
        head = re.split(r"\s{2,}", body[: m.start()].strip())[-1].strip()
        tail = re.sub(r"\([^)]*\)", "", body[m.start() + pf.end():]).strip()
        return {"teamA": head, "goalsA": int(pf.group(3)), "teamB": tail, "goalsB": int(pf.group(4)),
                "penA": int(pf.group(1)), "penB": int(pf.group(2)), "et": True}
    team_a = body[: m.start()].strip()
    team_a = re.split(r"\s{2,}", team_a)[-1].strip()
    rest = body[m.end():]
    vs = re.split(r"\s+v\s+", team_a)
    if len(vs) == 2:                       # "Brazil v Croatia  3-1"
        team_a, rest = vs[0].strip(), " " + vs[1] + " "
        out = {"teamA": team_a, "goalsA": int(m.group(1)), "teamB": None, "goalsB": int(m.group(2))}
        pen = PEN.search(body[m.end():])
        if pen:
            out["penA"], out["penB"] = int(pen.group(1)), int(pen.group(2))
        if re.search(r"a\.e\.t", body[m.end():]):
            out["et"] = True
        out["teamB"] = vs[1].strip()
        return out
    pen = PEN.search(rest)
    pens = None
    if pen:
        pens = (int(pen.group(1)), int(pen.group(2)))
        rest = rest[: pen.start()] + rest[pen.end():]
    et = bool(re.search(r"a\.e\.t", rest))
    rest = re.sub(r"a\.e\.t\.?", "", rest)
    rest = re.sub(r"\([^)]*\)", "", rest)
    team_b = rest.strip(" ,\t")
    if not team_a or not team_b or re.search(r"\d", team_b):
        return None
    out = {"teamA": team_a, "goalsA": int(m.group(1)), "teamB": team_b, "goalsB": int(m.group(2))}
    if pens:
        out["penA"], out["penB"] = pens
    if et:
        out["et"] = True
    return out


# Rounds whose source heading says "round"/"group" but that the ranking scores differently.
KNOCKOUT_FIRST_ROUND = {1934, 1938}        # first round was a straight knockout (scored as R16)
FINAL_ROUND_GROUP = {1950}                 # final round-robin, scored as the final (K=32)


def parse_worldcup_file(path, year, phase_override=None):
    phase = phase_override
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("▪"):
            head = line[1:].split("|")[0].strip()
            p = wc_phase(head)
            hl = head.lower()
            if year in KNOCKOUT_FIRST_ROUND and re.match(r"(first|preliminary) round", hl):
                p = "r16"
            elif year in FINAL_ROUND_GROUP and "final round" in hl:
                p = "final"
            if p:
                phase = p
            continue
        if phase is None or not line.strip() or line.lstrip().startswith(("#", "=")):
            continue
        if re.match(r"\s*(Group\s+\w+\s*\|)", line):
            continue
        m = parse_wc_match(line)
        if m:
            m["phase"] = phase
            m["year"] = year
            out.append(m)
    return out


def ucl_phase(h):
    h = h.lower()
    if "playoff" in h and "final" not in h or "play-off" in h:
        return "r16"          # knockout play-off round is scored as R16
    if "round of 16" in h:
        return "r16"
    if "quarter" in h:
        return "qf"
    if "semi" in h:
        return "sf"
    if h.endswith("final") or h.endswith("finals"):
        return "final"
    if "group" in h or "gruppe" in h or "league" in h:
        return "group"
    return None


def parse_ucl_file(path, season):
    phase = None
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("▪"):
            phase = ucl_phase(line[1:].strip())
            continue
        if phase is None or " v " not in line:
            continue
        line = re.sub(r"^\s*\d{1,2}:\d{2}\s+", "", line)
        left, right = re.split(r"\s+v\s+", line.strip(), maxsplit=1)
        m = SCORE.search(right)
        if not m:
            continue
        team_b = right[: m.start()].strip()
        rest = right[m.start():]
        pf = PEN_FIRST.match(rest)
        pens = None
        if pf:
            pens = (int(pf.group(1)), int(pf.group(2)))
            goals = (int(pf.group(3)), int(pf.group(4)))
        else:
            goals = (int(m.group(1)), int(m.group(2)))
            pen = PEN.search(rest)
            if pen:
                pens = (int(pen.group(1)), int(pen.group(2)))
        ca, cb = CC.search(left), CC.search(team_b)
        rec = {
            "season": season, "phase": phase,
            "teamA": CC.sub("", left).strip(), "goalsA": goals[0],
            "teamB": CC.sub("", team_b).strip(), "goalsB": goals[1],
        }
        if ca:
            rec["codeA"] = ca.group(1)
        if cb:
            rec["codeB"] = cb.group(1)
        if "a.e.t" in rest:
            rec["et"] = True
        if pens:
            rec["penA"], rec["penB"] = pens
        out.append(rec)
    return out


def parse_worldcup(root):
    root = Path(root)
    out = []
    for d in sorted(root.glob("[12][0-9][0-9][0-9]--*")):
        year = int(d.name[:4])
        for name in ("cup.txt", "cup_finals.txt"):
            f = d / name
            if f.exists():
                out.extend(parse_worldcup_file(f, year))
    return out


def parse_ucl(root, first_season="2011-12"):
    root = Path(root)
    out = []
    for d in sorted(root.glob("[12][0-9][0-9][0-9]-[0-9][0-9]")):
        if d.name < first_season or not (d / "cl.txt").exists():
            continue
        season = d.name[:4] + "/" + d.name[5:]
        out.extend(parse_ucl_file(d / "cl.txt", season))
    return out
