"""ELO engine. All clubs/nations start at INITIAL; K depends on the phase.

Result rule: a match decided in extra time counts by its extra-time score; if it
went to penalties the shoot-out winner counts as the winner (score 1 / 0),
so a team that advances never loses rating for a level 90/120 minutes.
"""
INITIAL = 1600


def result(m):
    """Score for team A: 1, 0.5 or 0."""
    if m.get("penA") is not None and m["penA"] != m.get("penB"):
        return 1.0 if m["penA"] > m["penB"] else 0.0
    if m["goalsA"] == m["goalsB"]:
        return 0.5
    return 1.0 if m["goalsA"] > m["goalsB"] else 0.0


def run(matches, phases, seed=()):
    """matches: chronological list with canonical teamA/teamB.
    Returns (ratings, counts, history) where history[i] = (eloA_after, eloB_after)."""
    elo = {t: INITIAL for t in seed}
    count = {}
    hist = []
    for m in matches:
        a, b = m["teamA"], m["teamB"]
        ra, rb = elo.setdefault(a, INITIAL), elo.setdefault(b, INITIAL)
        ea = 1 / (1 + 10 ** ((rb - ra) / 400))
        d = round(phases[m["phase"]]["k"] * (result(m) - ea))
        elo[a], elo[b] = ra + d, rb - d
        count[a] = count.get(a, 0) + 1
        count[b] = count.get(b, 0) + 1
        hist.append((elo[a], elo[b]))
    return elo, count, hist
