# Football ELO

ELO rankings for the UEFA Champions League (1992/93 →), the FIFA World Cup (1930 →), the English
top flight (First Division from 1888/89, Premier League from 1992/93) and the Polish top flight
(Liga 1927, I liga 1948–2008, Ekstraklasa 2008 →) and the UEFA Nations League (2018/19 →).
Static site on GitHub Pages; data refreshed daily by GitHub Actions.

```
data/matches/{ucl,wc,pl,ekstraklasa,nl}.json   matches exactly as imported (source names)
data/teams_{ucl,wc,pl,ekstraklasa,nl}.json  canonical team -> aliases (renames, successor states)
data/sync.json                  time of the last daily data check (shown on the home page)
data/phases.json             K-factor per phase
data/nl_leagues.json         Nations League editions (dates, 2018/19 divisions)
data/overrides.json          manual fixes: {"add": [...], "remove": [...]}
scripts/                     sync (import), build (ELO -> site/data), parsers, engine
site/                        the website (site/data/ is generated)
```

## Rules
- Start 1600; K per phase (`data/phases.json`); `R += K·(S−E)`.
- Extra time counts by its score; a match decided on penalties is a win for the shoot-out winner.
- Qualifying rounds are not rated. The Champions League knockout play-off round is rated as R16.
- Premier League and Ekstraklasa: one phase (`league`, K=16). Clubs keep their rating while outside the top flight.
- Nations League: one common ranking for all divisions; K by division (A 24 · B 12 · C 8 · D 4), quarter-finals K 24,
  semi-finals / 3rd place / final K 32, promotion/relegation play-offs between two divisions use the K of the lower one.
- Era buttons (Premier League: pre-1992 / 1992-; Ekstraklasa: pre-war / post-war) are filters over the years, not separate
  rankings: one continuous rating per club, shown as it stood at the end of the era; games and Δ count that era only.

## Data sources
- World Cup, Champions League 2011/12 →, Premier League 1992/93 →: [openfootball](https://github.com/openfootball) (daily).
- Premier League before 1992/93: [engsoccerdata](https://github.com/jalapic/engsoccerdata) `england.csv`, tier 1
  (frozen archive; for 1992/93–2024/25 it matches openfootball exactly, except 2022/23 which it lacks).
- Champions League 1992/93–2010/11: the original hand-entered data (frozen).
- Polish top flight 1927–: English Wikipedia season articles (results cross tables, CC BY-SA), read by
  `scripts/wikipedia_pl.py`; the two latest seasons are refreshed daily, and a season is never replaced by a
  copy with fewer matches. Seasons played in groups (1933, 1952, 1962) and the 1939 season cut short by the war
  have fewer matches than a full round robin by design.
- Nations League 2018/19 →: [international_results](https://github.com/martj42/international_results) (results and
  shoot-out winners, daily) plus the running edition from English Wikipedia (the dataset lags by weeks; a Wikipedia
  match is dropped as soon as the dataset has it). The dataset has no divisions or stages, so they are derived (`scripts/nationsleague.py`):
  groups = sets of teams that play each other in the league phase; 2018/19 divisions are listed in `data/nl_leagues.json`,
  later editions are inferred from promotion/relegation. A brand new edition needs no edit (it is detected and inferred);
  only the pre-declared editions in `nl_leagues.json` carry dates.
- Running season (UCL, Premier League): football-data.org when `FOOTBALL_DATA_KEY` is set.

## Editing team history
Edit `data/teams_*.json` on GitHub. Names under `aliases` are rated as the canonical team,
e.g. `"Serbia": {"aliases": ["Yugoslavia", "Serbia and Montenegro"]}`.
Ratings are recomputed from scratch on every build, so nothing else has to change.
Unknown names from the daily import are never guessed: the run stops and opens an issue listing them.

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

## Flags and logos
- National teams: `"iso"` in `data/teams_wc.json` (flagcdn.com code, e.g. `gb-eng`).
- Clubs: `"logo"` (image URL) in `data/teams_ucl.json`. Run the **Fetch club logos** workflow to fill
  missing ones from TheSportsDB; existing values are never overwritten, so any wrong logo can be fixed by hand.

## Current season fallback
openfootball can lag behind by weeks. If it has no matches for the running Champions League season,
`scripts/sync.py` takes them from football-data.org. Add a free API key as the repository secret
`FOOTBALL_DATA_KEY` (Settings → Secrets and variables → Actions) to enable it.
