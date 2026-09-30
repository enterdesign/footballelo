"""Live results from football-data.org (v4), used for the running season of a
competition (openfootball is often weeks behind). Needs a free API key
(env FOOTBALL_DATA_KEY). The free plan only covers the last few seasons.

Output records match scripts/openfootball.py: goals are the score after extra
time, penA/penB are the shoot-out goals.
"""
import json
import urllib.request

API = "https://api.football-data.org/v4/competitions/{comp}/matches?season={year}"
STAGES = {                                    # Champions League
    "LEAGUE_STAGE": "group", "GROUP_STAGE": "group",
    "PLAYOFFS": "r16", "LAST_16": "r16",
    "QUARTER_FINALS": "qf", "SEMI_FINALS": "sf", "FINAL": "final",
}
PL_STAGES = {"REGULAR_SEASON": "league"}      # Premier League


def fetch(year, key, comp="CL"):
    req = urllib.request.Request(API.format(comp=comp, year=year), headers={"X-Auth-Token": key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["matches"]


def convert(matches, season, stages=STAGES):
    out = []
    for m in matches:
        if m.get("status") != "FINISHED" or m.get("stage") not in stages:
            continue
        s = m["score"]
        home, away = m["homeTeam"]["name"], m["awayTeam"]["name"]
        rec = {"season": season, "phase": stages[m["stage"]], "teamA": home, "teamB": away}
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
