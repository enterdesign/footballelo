"""Champions League results from football-data.org (v4), used for seasons that
openfootball has not published yet. Needs a free API key (env FOOTBALL_DATA_KEY).

Output records match scripts/openfootball.py: goals are the score after extra
time, penA/penB are the shoot-out goals.
"""
import json
import urllib.request

API = "https://api.football-data.org/v4/competitions/CL/matches?season={year}"
STAGES = {
    "LEAGUE_STAGE": "group", "GROUP_STAGE": "group",
    "PLAYOFFS": "r16", "LAST_16": "r16",
    "QUARTER_FINALS": "qf", "SEMI_FINALS": "sf", "FINAL": "final",
}


def fetch(year, key):
    req = urllib.request.Request(API.format(year=year), headers={"X-Auth-Token": key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["matches"]


def convert(matches, season):
    out = []
    for m in matches:
        if m.get("status") != "FINISHED" or m.get("stage") not in STAGES:
            continue
        s = m["score"]
        home, away = m["homeTeam"]["name"], m["awayTeam"]["name"]
        rec = {"season": season, "phase": STAGES[m["stage"]], "teamA": home, "teamB": away}
        if s.get("duration") == "PENALTY_SHOOTOUT":
            # fullTime may include the shoot-out goals, so rebuild from the parts
            reg, ext, pen = s.get("regularTime") or {}, s.get("extraTime") or {}, s["penalties"]
            rec["goalsA"] = (reg.get("home") or 0) + (ext.get("home") or 0)
            rec["goalsB"] = (reg.get("away") or 0) + (ext.get("away") or 0)
            rec["penA"], rec["penB"], rec["et"] = pen["home"], pen["away"], True
        else:
            rec["goalsA"], rec["goalsB"] = s["fullTime"]["home"], s["fullTime"]["away"]
            if s.get("duration") == "EXTRA_TIME":
                rec["et"] = True
        out.append(rec)
    return out
