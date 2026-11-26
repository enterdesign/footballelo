"""Static, crawlable pages for single teams (clubs and national teams): "Real Madrid ELO rating", "Elo de Brasil", ...

The interactive app shows a team's history only behind a #hash route, which Google does not index. These pages repeat the most
useful part of it as plain HTML: current rating and rank, all-time high, record, a rating chart (inline SVG), the last matches,
a season-by-season table, the team's place in every ranking it is in and its neighbours in the table.
Generated into site/{teams,es/equipos,pt/equipes,pl/druzyny}/ on every build (git-ignored), called from seo.generate().
"""
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote

import seo

e = seo.e
LEAGUES = ("pl", "ekstraklasa", "bundesliga", "spain", "france", "italy")
# how many of the best teams of each ranking get a page of their own
SELECT = {**{k: 30 for k in LEAGUES}, "uefa": 40, "wc": 50}
DIRS = {"en": "teams", "es": "equipos", "pt": "equipes", "pl": "druzyny"}
RECENT = 10
WDL = {"en": dict(W="W", D="D", L="L"), "es": dict(W="G", D="E", L="P"), "pt": dict(W="V", D="E", L="D"), "pl": dict(W="W", D="R", L="P")}   # result letters
SEP = {"en": ",", "es": ".", "pt": ".", "pl": "\u00a0"}                  # thousands separator per language

TT = {
    "en": {"title_short": "{name} ELO rating", "title": "{name} ELO rating and history since {first}", "h1": "{name} ELO rating",
           "desc": "{name} ELO rating: {elo}, ranked {rank} of {n} in the {rname} ELO ranking. Highest rating {ath} ({ath_per}). {m} matches rated since {first}. Updated daily.",
           "desc_start": "{name} ELO rating: {elo}, ranked {rank} of {n} in the {rname} ELO ranking. {m} matches rated since {first}. Updated daily.",
           "lead": "{name} has a current ELO rating of <b>{elo}</b>, ranked <b>{rank}</b> of {n} in the {rname} ELO ranking. The rating is rebuilt from every match since {first} and refreshed daily.",
           "all": "← All rankings", "open": "Open the interactive history of {name}",
           "current": "Current ELO", "rank": "Rank", "ath": "All-time high", "matches": "Matches", "record": "Won / drawn / lost",
           "chart_h": "Rating history", "recent_h": "Latest matches", "seasons_h": "Season by season", "other_h": "{name} in the ELO rankings",
           "near_h": "Closest in the {rname} ranking", "season": "Season", "year": "Year", "start": "Start", "end": "End", "games": "Matches",
           "phase": "Stage", "opponent": "Opponent", "result": "Result", "elo_after": "ELO after", "ranking": "Ranking", "start_rating": "starting rating, never exceeded",
           "chart_alt": "ELO rating of {name} by {unit}, from {lo} to {hi}", "unit_s": "season", "unit_y": "year"},
    "es": {"title_short": "Elo de {name}", "title": "Elo de {name}: ranking e historial desde {first}", "h1": "Elo de {name}",
           "desc": "Elo de {name}: {elo} puntos, puesto {rank} de {n} en el ranking Elo: {rname}. Máximo histórico {ath} ({ath_per}). {m} partidos valorados desde {first}. Actualizado a diario.",
           "desc_start": "Elo de {name}: {elo} puntos, puesto {rank} de {n} en el ranking Elo: {rname}. {m} partidos valorados desde {first}. Actualizado a diario.",
           "lead": "{name} tiene una puntuación Elo actual de <b>{elo}</b> y ocupa el puesto <b>{rank}</b> de {n} en el ranking Elo: {rname}. La puntuación se recalcula con todos los partidos desde {first} y se actualiza a diario.",
           "all": "← Todos los rankings", "open": "Abrir el historial interactivo de {name}",
           "current": "Elo actual", "rank": "Puesto", "ath": "Máximo histórico", "matches": "Partidos", "record": "Ganados / empatados / perdidos",
           "chart_h": "Evolución de la puntuación", "recent_h": "Últimos partidos", "seasons_h": "Temporada a temporada", "other_h": "{name} en los rankings Elo",
           "near_h": "Más cerca en el ranking Elo: {rname}", "season": "Temporada", "year": "Año", "start": "Inicio", "end": "Final", "games": "Partidos",
           "phase": "Fase", "opponent": "Rival", "result": "Resultado", "elo_after": "Elo después", "ranking": "Ranking", "start_rating": "puntuación inicial, nunca superada",
           "chart_alt": "Puntuación Elo de {name} por {unit}, de {lo} a {hi}", "unit_s": "temporada", "unit_y": "año"},
    "pt": {"title_short": "Elo: {name}", "title": "Elo: {name}, ranking e histórico desde {first}", "h1": "Elo: {name}",
           "desc": "Elo: {name} tem {elo} pontos, posição {rank} de {n} no ranking Elo: {rname}. Máximo histórico {ath} ({ath_per}). {m} jogos avaliados desde {first}. Atualizado diariamente.",
           "desc_start": "Elo: {name} tem {elo} pontos, posição {rank} de {n} no ranking Elo: {rname}. {m} jogos avaliados desde {first}. Atualizado diariamente.",
           "lead": "{name} tem uma pontuação Elo atual de <b>{elo}</b> e ocupa a posição <b>{rank}</b> de {n} no ranking Elo: {rname}. A pontuação é recalculada com todos os jogos desde {first} e atualizada diariamente.",
           "all": "← Todos os rankings", "open": "Abrir o histórico interativo de {name}",
           "current": "Elo atual", "rank": "Posição", "ath": "Máximo histórico", "matches": "Jogos", "record": "Vitórias / empates / derrotas",
           "chart_h": "Evolução da pontuação", "recent_h": "Últimos jogos", "seasons_h": "Temporada a temporada", "other_h": "{name} nos rankings Elo",
           "near_h": "Mais perto no ranking Elo: {rname}", "season": "Temporada", "year": "Ano", "start": "Início", "end": "Fim", "games": "Jogos",
           "phase": "Fase", "opponent": "Adversário", "result": "Resultado", "elo_after": "Elo depois", "ranking": "Ranking", "start_rating": "pontuação inicial, nunca superada",
           "chart_alt": "Pontuação Elo de {name} por {unit}, de {lo} a {hi}", "unit_s": "temporada", "unit_y": "ano"},
    "pl": {"title_short": "Elo {name}", "title": "Elo {name}: ranking i historia od {first}", "h1": "Elo {name}",
           "desc": "Elo {name}: {elo} pkt, miejsce {rank} z {n} w rankingu Elo: {rname}. Rekord wszech czasów {ath} ({ath_per}). Ocenionych meczów: {m} od {first}. Aktualizowane codziennie.",
           "desc_start": "Elo {name}: {elo} pkt, miejsce {rank} z {n} w rankingu Elo: {rname}. Ocenionych meczów: {m} od {first}. Aktualizowane codziennie.",
           "lead": "{name} ma obecnie <b>{elo}</b> punktów Elo i zajmuje miejsce <b>{rank}</b> z {n} w rankingu Elo: {rname}. Punktacja jest przeliczana z wszystkich meczów od {first} i odświeżana codziennie.",
           "all": "← Wszystkie rankingi", "open": "Otwórz interaktywną historię: {name}",
           "current": "Obecne Elo", "rank": "Miejsce", "ath": "Rekord wszech czasów", "matches": "Mecze", "record": "Wygrane / remisy / porażki",
           "chart_h": "Historia punktacji", "recent_h": "Ostatnie mecze", "seasons_h": "Sezon po sezonie", "other_h": "{name} w rankingach Elo",
           "near_h": "Najbliżej w rankingu: {rname}", "season": "Sezon", "year": "Rok", "start": "Początek", "end": "Koniec", "games": "Mecze",
           "phase": "Faza", "opponent": "Rywal", "result": "Wynik", "elo_after": "Elo po meczu", "ranking": "Ranking", "start_rating": "punktacja początkowa, nigdy nie przekroczona",
           "chart_alt": "Punktacja Elo: {name} według {unit}, od {lo} do {hi}", "unit_s": "sezonów", "unit_y": "lat"},
}


HUB = {
    "en": {"nav": "All teams", "title": "All teams: football ELO ratings", "h1": "All teams",
           "desc": "Football ELO ratings of {n} clubs and national teams: the current rating, rank and full history of every team, grouped by ranking.",
           "intro": "Every team below has its own page with the current ELO rating, rank, all-time high, a rating chart, the latest matches and a season-by-season table."},
    "es": {"nav": "Todos los equipos", "title": "Todos los equipos: Elo de fútbol", "h1": "Todos los equipos",
           "desc": "Elo de fútbol de {n} clubes y selecciones: puntuación actual, puesto e historial completo de cada equipo, agrupados por ranking.",
           "intro": "Cada equipo tiene su página con la puntuación Elo actual, el puesto, el máximo histórico, un gráfico, los últimos partidos y una tabla temporada a temporada."},
    "pt": {"nav": "Todas as equipes", "title": "Todas as equipes: Elo do futebol", "h1": "Todas as equipes",
           "desc": "Elo do futebol de {n} clubes e seleções: pontuação atual, posição e histórico completo de cada equipe, agrupados por ranking.",
           "intro": "Cada equipe tem a sua página com a pontuação Elo atual, a posição, o máximo histórico, um gráfico, os últimos jogos e uma tabela temporada a temporada."},
    "pl": {"nav": "Wszystkie zespoły", "title": "Wszystkie zespoły: Elo piłki nożnej", "h1": "Wszystkie zespoły",
           "desc": "Elo piłki nożnej {n} klubów i reprezentacji: obecna punktacja, miejsce i pełna historia każdego zespołu, pogrupowane według rankingów.",
           "intro": "Każdy zespół ma własną stronę z obecną punktacją Elo, miejscem, rekordem wszech czasów, wykresem, ostatnimi meczami i tabelą sezon po sezonie."},
}


def hub_url(lang):
    return f"{seo.BASE}{DIRS[lang]}/" if lang == "en" else f"{seo.BASE}{lang}/{DIRS[lang]}/"


def dname(name, lang, ctx):
    """Name of a team in a language: national teams are translated, clubs keep their name."""
    return ctx["names"].get(lang, {}).get(name, name) if lang != "en" and name in ctx["nation_names"] else name


def hub_page(lang, ctx):
    """One crawlable list of every team page, grouped by ranking: a path for search engines (and people) to all of them."""
    h, t = HUB[lang], TT[lang]
    datas, ents = ctx["datas"], ctx["ents"]
    by = {}
    for ent in ents.values():
        by.setdefault(ent["main"], []).append(ent)
    secs = ""
    for key in seo.SLUGS:
        if key not in by:
            continue
        rows = sorted(by[key], key=lambda x: -datas[key]["teams"][x["places"][key]]["elo"])
        lis = "".join(f'<li><a href="{x["slug"]}.html">{e(dname(x["name"], lang, ctx))}</a></li>' for x in rows)
        secs += (f'<h2 style="font:700 20px var(--display);margin:24px 0 8px"><a href="../rankings/{seo.SLUGS_BY[lang][key]}.html">{e(ctx["rnames"][lang][key])}</a></h2>'
                 f'<ul class="hub">{lis}</ul>')
    url = hub_url(lang)
    alts = [(l, hub_url(l)) for l in seo.LANGS] + [("x-default", hub_url("en"))]
    css = "../style.css" if lang == "en" else "../../style.css"
    desc = h["desc"].format(n=len(ents))
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": h["title"], "url": url, "inLanguage": lang, "description": desc}
    switch = " · ".join(f'<a href="{hub_url(l)}" hreflang="{l}" lang="{l}">{seo.TX[l]["name"]}</a>' for l in seo.LANGS if l != lang)
    return seo.head(lang, h["title"], desc, url, alts, css, ld) + f"""<body>
<a id="brand" href="../">Football <span>ELO</span></a>
<style>ul.hub{{list-style:none;columns:220px;column-gap:24px;padding:0}}ul.hub li{{padding:3px 0;break-inside:avoid}}ul.hub a:hover,h2 a:hover{{color:var(--accent)}}</style>
<main>
<p class="eyebrow"><a href="../">{t["all"]}</a> · {switch}</p>
<h1 class="title" style="font-size:44px">{e(h["h1"])}</h1>
<p>{e(desc)}</p>
<p>{e(h["intro"])}</p>
{secs}
</main>
</body>
</html>
"""


def slugify(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def country_names(i18n_js):
    """National team names per language, read from the dictionary the app uses (i18n.js, section `country`)."""
    text = Path(i18n_js).read_text(encoding="utf-8")
    block = text[text.index("  country: {"):]
    out = {}
    for lang in seo.LANGS[1:]:
        m = re.search(rf"^    {lang}: (\{{.*\}}),\s*$", block, re.M)
        out[lang] = json.loads(m.group(1)) if m else {}
    return out


def team_url(slug, lang):
    return f"{seo.BASE}{DIRS[lang]}/{slug}.html" if lang == "en" else f"{seo.BASE}{lang}/{DIRS[lang]}/{slug}.html"


def build_index(datas):
    """Teams that get a page: the best of every league, of the UEFA club ranking and of the World Cup ranking."""
    where = {}                                              # name -> {ranking key: index in its team list}
    for key, d in datas.items():
        for i, t in enumerate(d["teams"]):
            where.setdefault(t["name"], {})[key] = i
    chosen = []
    for key, n in SELECT.items():
        if key in datas:
            chosen += [t["name"] for t in datas[key]["teams"][:n]]
    ents = {}
    for name in dict.fromkeys(chosen):
        places = where[name]
        main = max(places, key=lambda k: datas[k]["teams"][places[k]]["matches"])
        if datas[main]["teams"][places[main]]["matches"] == 0:
            continue
        ents[name] = {"name": name, "slug": slugify(name), "places": places, "main": main, "nation": main in seo.NATIONS}
    return ents


def timeline(d, idx):
    """[(period, phase, opponent index, goals for, goals against, won?, rating after, opponent rating after)] of one team."""
    rows = []
    for per, ph, a, ga, b, gb, dec, pa, pb, ea, eb in (m[:11] for m in d["matches"]):
        if idx not in (a, b):
            continue
        home = idx == a
        gf, gg = (ga, gb) if home else (gb, ga)
        if gf == gg and pa is not None and pb is not None and pa != pb:           # drawn, decided on penalties
            res = "W" if ((pa > pb) == home) else "L"
        else:
            res = "W" if gf > gg else "L" if gf < gg else "D"
        rows.append((per, ph, b if home else a, gf, gg, res, ea if home else eb, eb if home else ea))
    return rows


def seasons(rows):
    out = {}
    start = 1600
    for per, _, _, _, _, _, after, _ in rows:
        s = out.setdefault(per, {"start": start, "n": 0})
        s["end"] = after
        s["n"] += 1
        start = after
    return out


def chart(per_end, name, t, unit):
    pts = list(per_end.values())
    if len(pts) < 2:
        return ""
    w, h, pad = 720, 220, 34
    lo, hi = min(pts), max(pts)
    span = max(hi - lo, 1)
    xs = [pad + (w - 2 * pad) * i / (len(pts) - 1) for i in range(len(pts))]
    ys = [h - pad - (h - 2 * pad) * (v - lo) / span for v in pts]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    labels = list(per_end)
    alt = t["chart_alt"].format(name=name, unit=unit, lo=lo, hi=hi)
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{e(alt)}" style="width:100%;height:auto;max-width:720px;background:var(--panel);border:1px solid var(--rule)">'
            f'<line x1="{pad}" y1="{h - pad}" x2="{w - pad}" y2="{h - pad}" stroke="var(--rule2)"/><line x1="{pad}" y1="{pad}" x2="{w - pad}" y2="{pad}" stroke="var(--rule)"/>'
            f'<polyline points="{line}" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="3.5" fill="var(--accent)"/>'
            f'<g font-family="var(--display)" font-size="13" fill="var(--mute)"><text x="4" y="{pad + 4}">{hi}</text><text x="4" y="{h - pad + 4}">{lo}</text>'
            f'<text x="{pad}" y="{h - 10}">{e(labels[0])}</text><text x="{w - pad}" y="{h - 10}" text-anchor="end">{e(labels[-1])}</text></g></svg>')


def page(ent, lang, ctx):
    """ctx: datas, ents, names (translated national teams), rnames (ranking names per language)."""
    t = TT[lang]
    datas, ents = ctx["datas"], ctx["ents"]
    nation = ent["nation"]
    key = ent["main"]
    d = datas[key]
    idx = ent["places"][key]
    team = d["teams"][idx]
    disp = lambda n: (ctx["names"].get(lang, {}).get(n, n) if lang != "en" and n in ctx["nation_names"] else n)
    name = disp(ent["name"])
    rows = timeline(d, idx)
    per = seasons(rows)
    first = rows[0][0]
    elo = team["elo"]
    rank = 1 + sum(1 for x in d["teams"] if x["elo"] > elo)
    n = len(d["teams"])
    rname = ctx["rnames"][lang][key]
    best = max(rows, key=lambda r: r[6])
    ath_start = best[6] <= 1600
    w, dr, lo = (sum(1 for r in rows if r[5] == c) for c in "WDL")
    unit = t["unit_y"] if nation else t["unit_s"]
    fmt = dict(name=name, elo=elo, rank=rank, n=n, rname=rname, first=first, m=f"{len(rows):,}".replace(",", SEP[lang]), ath=best[6], ath_per=best[0])
    title = t["title"].format(**fmt)
    if len(title) > 66:                                        # very long club names: drop the "since ..." part so Google does not cut the title
        title = t["title_short"].format(**fmt)
    desc = (t["desc_start"] if ath_start else t["desc"]).format(**fmt)
    url = team_url(ent["slug"], lang)
    alts = [(l, team_url(ent["slug"], l)) for l in seo.LANGS] + [("x-default", team_url(ent["slug"], "en"))]
    css = "../style.css" if lang == "en" else "../../style.css"
    ld = {"@context": "https://schema.org", "@type": "SportsTeam", "name": ent["name"], "sport": "Association football", "url": url, "inLanguage": lang,
          "description": desc}
    fe = {k: e(str(v)) for k, v in fmt.items()}                # values that go into the HTML body
    link = lambda nm: (f'<a href="{ctx["ents"][nm]["slug"]}.html">{e(disp(nm))}</a>' if nm in ents else e(disp(nm)))
    # last matches
    rec = "".join(
        f"<tr><td>{e(r[0])}</td><td>{e(d['phases'].get(r[1], {}).get('label', r[1]))}</td><td>{link(d['teams'][r[2]]['name'])}</td>"
        f"<td>{WDL[lang][r[5]]} {r[3]}-{r[4]}</td><td>{r[6]}</td></tr>" for r in reversed(rows[-RECENT:]))
    srows = "".join(
        f"<tr><td>{e(p)}</td><td>{s['start']}</td><td>{s['end']}</td><td>{s['end'] - s['start']:+d}</td><td>{s['n']}</td></tr>" for p, s in reversed(per.items()))
    others = "".join(
        f'<tr><td><a href="../rankings/{seo.SLUGS_BY[lang][k]}.html">{e(ctx["rnames"][lang][k])}</a></td>'
        f'<td>{1 + sum(1 for x in datas[k]["teams"] if x["elo"] > datas[k]["teams"][i]["elo"])} / {len(datas[k]["teams"])}</td><td>{datas[k]["teams"][i]["elo"]}</td></tr>'
        for k, i in sorted(ent["places"].items(), key=lambda kv: kv[0] != key))
    near = "".join(f"<li>{link(x['name'])} <span class=\"mono\">{x['elo']}</span></li>"
                   for x in d["teams"][max(0, rank - 4):rank + 3] if x["name"] != ent["name"])
    switch = " · ".join(f'<a href="{team_url(ent["slug"], l)}" hreflang="{l}" lang="{l}">{seo.TX[l]["name"]}</a>' for l in seo.LANGS if l != lang)
    comp_url = f"../#{key}/stats/{quote(ent['name'], safe='')}"
    ath_txt = f"{best[6]} ({e(best[0])})" if not ath_start else f"1600 ({t['start_rating']})"
    th = lambda *c: "<tr>" + "".join(f"<th>{x}</th>" for x in c) + "</tr>"
    h2 = 'style="font:700 20px var(--display);margin:24px 0 6px"'
    return seo.head(lang, title, desc, url, alts, css, ld) + f"""<body>
<a id="brand" href="../">Football <span>ELO</span></a>
<main>
<p class="eyebrow"><a href="../">{t["all"]}</a> · <a href="../rankings/{seo.SLUGS_BY[lang][key]}.html">{e(rname)}</a> · <a href="./">{e(HUB[lang]["nav"])}</a> · {switch}</p>
<h1 class="title" style="font-size:44px">{e(t["h1"].format(name=name))}</h1>
<p>{t["lead"].format(**fe)}</p>
<a class="open" href="{comp_url}">{e(t["open"].format(name=name))}</a>
<table class="seo"><tr><th>{t["current"]}</th><th>{t["rank"]}</th><th>{t["ath"]}</th><th>{t["matches"]}</th><th>{t["record"]}</th></tr>
<tr><td><b>{elo}</b></td><td>{rank} / {n}</td><td>{ath_txt}</td><td>{fmt["m"]}</td><td>{w} / {dr} / {lo}</td></tr></table>
<h2 {h2}>{t["chart_h"]}</h2>
{chart({p: s["end"] for p, s in per.items()}, name, t, unit)}
<h2 {h2}>{t["recent_h"]}</h2>
<table class="seo">{th("&nbsp;", t["phase"], t["opponent"], t["result"], t["elo_after"])}{rec}</table>
<h2 {h2}>{t["seasons_h"]}</h2>
<table class="seo">{th(t["year"] if nation else t["season"], t["start"], t["end"], "Δ", t["games"])}{srows}</table>
<h2 {h2}>{e(t["other_h"].format(name=name))}</h2>
<table class="seo">{th(t["ranking"], t["rank"], "Elo")}{others}</table>
<h2 {h2}>{e(t["near_h"].format(rname=rname))}</h2>
<ul>{near}</ul>
</main>
</body>
</html>
"""


def generate(site, datas):
    """Writes every team page and returns {lang: {team name: relative href}} (for links from the ranking pages) and the page URLs."""
    site = Path(site)
    ents = build_index(datas)
    names = country_names(site / "i18n.js") if (site / "i18n.js").exists() else {}
    nation_names = {t["name"] for k in seo.NATIONS if k in datas for t in datas[k]["teams"]}
    rnames = {"en": {k: re.sub(r"\s*\([^)]*\)", "", d["title"]).strip() for k, d in datas.items()}}
    for lang in seo.LANGS[1:]:
        rnames[lang] = {k: re.sub(r"\s*\([^)]*\)", "", seo.SHORT[lang][k]).strip() for k in datas}
    ctx = {"datas": datas, "ents": ents, "names": names, "nation_names": nation_names, "rnames": rnames}
    links, urls = {l: {} for l in seo.LANGS}, []
    for lang in seo.LANGS:
        out = site / DIRS[lang] if lang == "en" else site / lang / DIRS[lang]
        out.mkdir(parents=True, exist_ok=True)
        for ent in ents.values():
            (out / f"{ent['slug']}.html").write_text(page(ent, lang, ctx), encoding="utf-8")
            links[lang][ent["name"]] = f"../{DIRS[lang]}/{ent['slug']}.html"
            urls.append(team_url(ent["slug"], lang))
        (out / "index.html").write_text(hub_page(lang, ctx), encoding="utf-8")
        urls.append(hub_url(lang))
    return links, urls
