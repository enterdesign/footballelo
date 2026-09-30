# Football ELO

ELO rankings for the UEFA Champions League (1992/93 →) and the FIFA World Cup (1930 →).
Static site on GitHub Pages; data refreshed weekly by GitHub Actions.

```
data/matches/{ucl,wc}.json   matches exactly as imported (source names)
data/teams_{ucl,wc}.json     canonical team -> aliases (renames, successor states)
data/phases.json             K-factor per phase
data/overrides.json          manual fixes: {"add": [...], "remove": [...]}
scripts/                     sync (import), build (ELO -> site/data), parsers, engine
site/                        the website (site/data/ is generated)
```

## Rules
- Start 1600; K per phase (`data/phases.json`); `R += K·(S−E)`.
- Extra time counts by its score; a match decided on penalties is a win for the shoot-out winner.
- Qualifying rounds are not rated. The Champions League knockout play-off round is rated as R16.

## Editing team history
Edit `data/teams_*.json` on GitHub. Names under `aliases` are rated as the canonical team,
e.g. `"Serbia": {"aliases": ["Yugoslavia", "Serbia and Montenegro"]}`.
Ratings are recomputed from scratch on every build, so nothing else has to change.
Unknown names from the weekly import are never guessed: the run stops and opens an issue listing them.

## Manual match fixes
`data/overrides.json` → `add` takes match objects like
`{"season":"2025/26","phase":"group","teamA":"…","goalsA":1,"teamB":"…","goalsB":0}` (WC uses `"year"`),
`remove` takes any subset of fields that identifies the match. Add `"penA"`/`"penB"` for a shoot-out.

## Local use
```
python scripts/sync.py     # optional: refresh from openfootball
python scripts/build.py    # writes site/data/*.json
python -m http.server -d site
python -m unittest discover -s tests
```

## Setup (once)
Repo → Settings → Pages → Source: **GitHub Actions**.
