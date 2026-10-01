"""European Championship and Copa América from the open `international_results` dataset.

The dataset has no stage names, so they are assigned by position in the (chronological) list of an
edition, from the known format of each era. An edition that is still being played is just a prefix
of its format. Edition label = year of the tournament (Euro 2020, played in 2021, is labelled "2020").
"""
import nationsleague

EURO = "UEFA Euro"
COPA = "Copa América"
COPA_FIRST = 1993          # earlier Copa América editions are not included
EURO_LABEL = {"2021": "2020"}
COPA_GROUP_MATCHES = {2021: 20}      # 10 teams in two groups of five; 18 for 12 teams, 24 for 16 teams


def euro_stages(year):
    if year <= 1976:
        return ["sf", "sf", "3rd", "final", "final"]          # 1968 had a replayed final
    if year == 1980:
        return ["group"] * 12 + ["3rd", "final"]
    if year <= 1992:
        return ["group"] * 12 + ["sf", "sf", "final"]
    if year <= 2012:
        return ["group"] * 24 + ["qf"] * 4 + ["sf"] * 2 + ["final"]
    return ["group"] * 36 + ["r16"] * 8 + ["qf"] * 4 + ["sf"] * 2 + ["final"]


def copa_stages(year):
    g = COPA_GROUP_MATCHES.get(year, 18 if year <= 2019 else 24)
    if year in (2016, 2024):
        g = 24
    return ["group"] * g + ["qf"] * 4 + ["sf"] * 2 + ["3rd", "final"]


def prepare(key, raw):
    """Raw matches (dated, chronological) -> matches with "year" (edition) and "phase"."""
    out, by = [], {}
    for m in raw:
        y = int(m["date"][:4])
        if key == "copa" and y < COPA_FIRST:
            continue
        by.setdefault(y, []).append(m)
    for y, ms in sorted(by.items()):
        stages = euro_stages(y) if key == "euro" else copa_stages(y)
        label = EURO_LABEL.get(str(y), str(y)) if key == "euro" else str(y)
        for i, m in enumerate(ms):
            out.append({**m, "year": label, "phase": stages[min(i, len(stages) - 1)]})
    return out
