"""Static, crawlable pages for search engines (the site itself is a single-page app with #hash routes,
which Google does not index as separate pages).

Generated into site/ on every build (and git-ignored): one page per ranking with its own title, description
and the top of the table as plain HTML, in English (rankings/) and Spanish (es/), plus sitemap.xml.
The interactive app stays English; the Spanish pages link to it.
"""
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://enterdesign.github.io/footballelo/"
SLUGS = {"wc": "world-cup", "euro": "european-championship", "copa": "copa-america", "nl": "nations-league",
         "ucl": "champions-league", "el": "europa-league", "conf": "conference-league",
         "uefa": "uefa-club-competitions", "pl": "premier-league", "ekstraklasa": "ekstraklasa", "bundesliga": "bundesliga", "spain": "la-liga", "france": "ligue-1", "italy": "serie-a"}
SLUGS_ES = {"wc": "copa-del-mundo", "euro": "eurocopa", "copa": "copa-america", "nl": "liga-de-naciones",
            "ucl": "liga-de-campeones", "el": "liga-europa", "conf": "liga-conferencia",
            "uefa": "competiciones-uefa-de-clubes", "pl": "premier-league", "ekstraklasa": "ekstraklasa",
            "bundesliga": "bundesliga", "spain": "la-liga", "france": "ligue-1", "italy": "serie-a"}
SHORT_ES = {"wc": "Mundial de fútbol (Copa del Mundo)", "euro": "Eurocopa", "copa": "Copa América", "nl": "Liga de Naciones",
            "ucl": "Liga de Campeones", "el": "Liga Europa", "conf": "Liga Conferencia", "uefa": "competiciones UEFA de clubes",
            "pl": "Premier League", "ekstraklasa": "Ekstraklasa", "bundesliga": "Bundesliga", "spain": "La Liga",
            "france": "Ligue 1", "italy": "Serie A"}
# English titles of the pages that match what people search for ("elo champions league", "world football elo ratings", ...)
EN_TITLES = {"uefa": "UEFA club ELO ranking: Champions League, Europa League & Conference League",
             "ucl": "Champions League ELO ranking – ELO ratings of every club since {first}",
             "wc": "World football ELO ratings – national team ELO ranking since {first}"}
NATIONS = {"wc", "euro", "copa", "nl"}
TOP = 50
e = html.escape

TX = {
    "en": {"lang": "en", "all": "← All rankings", "open": "Open the interactive ranking", "top": "Top {n}", "name": "Name",
           "country": "Country", "region": "Region", "elo": "ELO", "matches": "Matches",
           "about_h": "About this football ELO ranking", "how_h": "How the rating works", "all_label": "All rankings", "home": "home"},
    "es": {"lang": "es", "all": "← Todos los rankings", "open": "Abrir el ranking interactivo", "top": "Top {n}", "name": "Nombre",
           "country": "País", "region": "Región", "elo": "Elo", "matches": "Partidos",
           "about_h": "Sobre este ranking Elo de fútbol", "how_h": "Cómo funciona la puntuación", "all_label": "Todos los rankings", "home": "inicio"},
}


def url_of(key, lang):
    return f"{BASE}rankings/{SLUGS[key]}.html" if lang == "en" else f"{BASE}es/rankings/{SLUGS_ES[key]}.html"


def span(d):
    return d["matches"][0][0], d["matches"][-1][0]


def describe(d, key):
    first, last = span(d)
    top = ", ".join(f"{t['name']} ({t['elo']})" for t in d["teams"][:3])
    n, m = len(d["teams"]), f"{len(d['matches']):,}"
    if key == "wc":
        return (f"World football ELO ratings and rankings of national teams: FIFA World Cup ELO ranking of {n} nations "
                f"from {first} to {last}, {m} matches rated. Top now: {top}. Updated daily.")
    if key == "uefa":
        return (f"UEFA ELO ranking of clubs: one ELO rating across the Champions League, Europa League and Conference League "
                f"({n} clubs, {m} matches from {first} to {last}). Top now: {top}. Updated daily.")
    noun = "national teams" if key in NATIONS else "clubs"
    return (f"{d['title']} ELO ranking: ratings of {n} {noun} from {first} to {last}, "
            f"{m} matches rated. Top now: {top}. Updated daily.")


def describe_es(d, key):
    first, last = span(d)
    top = ", ".join(f"{t['name']} ({t['elo']})" for t in d["teams"][:3])
    noun = "selecciones" if key in NATIONS else "clubes"
    return (f"Ranking Elo – {SHORT_ES[key]}: puntuación Elo de {len(d['teams'])} {noun} de {first} a {last}, "
            f"{len(d['matches']):,} partidos valorados. Líderes actuales: {top}. Actualizado a diario.")


def head(lang, title, desc, url, alts, css, ld):
    links = "\n".join(f'<link rel="alternate" hreflang="{h}" href="{u}">' for h, u in alts)
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
{links}
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{css}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>main{{max-width:960px;margin:0 auto;padding:22px 16px 60px}}table.seo{{width:100%;border-collapse:collapse;font:400 15px var(--body)}}
table.seo th{{text-align:left;font:600 14px var(--display);color:var(--mute);border-bottom:1px solid var(--ink);padding:6px 8px}}
table.seo td{{padding:6px 8px;border-bottom:1px solid var(--rule)}}.open{{display:inline-block;margin:12px 0 18px;padding:8px 16px;background:var(--ink);color:#fff;font:600 16px var(--display)}}</style>
</head>
"""


def page(key, d, lang="en"):
    t = TX[lang]
    url = url_of(key, lang)
    other = "es" if lang == "en" else "en"
    first, last = span(d)
    n, m = len(d["teams"]), f"{len(d['matches']):,}"
    if lang == "en":
        desc = describe(d, key)
        title = f"{d['title']} ELO ranking"
        full_title = EN_TITLES[key].format(first=first) if key in EN_TITLES else f"{title} – football ELO ratings since {first}"
        noun = "national teams" if key in NATIONS else "clubs"
        slugs = SLUGS
        switch = f'<a href="{url_of(key, "es")}" hreflang="es" lang="es">Español</a>'
        back, open_href = "../", f"../#{key}"
        nav_names = {k: s.replace("-", " ").title() for k, s in SLUGS.items()}
        about = (f"This is a football ELO ranking of {n} {noun}, rated match by match from {e(first)} to {e(last)} ({m} matches). "
                 "Every team has one continuous ELO rating, so the numbers can be compared across seasons. The ranking is rebuilt from the full "
                 "match history and refreshed daily. In the interactive version you can see the rating history of each team, its all-time high "
                 "rating, season-by-season changes, every match with the rating after it, and head-to-head comparisons.")
        ks = ", ".join(f"{e(p['label'])} {p['k']}" for p in d["phases"].values())
        how = ("Every team starts at 1600. After each match R ← R + K × (S − E), where E = 1 / (1 + 10^((R<sub>opponent</sub> − R) / 400)) and S is 1 "
               "for a win, 0.5 for a draw, 0 for a loss. A match decided on penalties counts as a win for the shoot-out winner. "
               f"K-factors by stage: {ks}.")
    else:
        desc = describe_es(d, key)
        title = f"Ranking Elo – {SHORT_ES[key]}"
        full_title = f"{title}: clasificación Elo de fútbol desde {first}"
        noun = "selecciones" if key in NATIONS else "clubes"
        slugs = SLUGS_ES
        switch = f'<a href="{url_of(key, "en")}" hreflang="en" lang="en">English</a>'
        back, open_href = "../", f"../#{key}"
        nav_names = {k: SHORT_ES[k] for k in SLUGS_ES}
        about = (f"Este es un ranking Elo de fútbol de {n} {noun}, calculado partido a partido de {e(first)} a {e(last)} ({m} partidos). "
                 "Cada equipo tiene una puntuación Elo continua, por lo que los valores se pueden comparar entre temporadas. El ranking se recalcula "
                 "con todo el historial de partidos y se actualiza a diario. En la versión interactiva puedes ver el historial de cada "
                 "equipo, su máxima puntuación histórica, los cambios temporada a temporada, cada partido con la puntuación posterior y comparaciones cara a cara.")
        ks = ", ".join(f"{e(p['label'])} {p['k']}" for p in d["phases"].values())
        how = ("Todos los equipos empiezan con 1600 puntos. Tras cada partido: R ← R + K × (S − E), donde E = 1 / (1 + 10^((R<sub>rival</sub> − R) / 400)) "
               "y S es 1 por victoria, 0,5 por empate y 0 por derrota. Un partido decidido en penaltis cuenta como victoria para el ganador de la tanda. "
               f"Factores K por fase: {ks}.")
    rows = "".join(
        f"<tr><td>{i}</td><td>{e(x['name'])}</td><td>{e(x.get('country') or x.get('label') or '')}</td>"
        f"<td>{x['elo']}</td><td>{x['matches']}</td></tr>" for i, x in enumerate(d["teams"][:TOP], 1))
    nav = " · ".join(f'<a href="{slugs[k]}.html">{e(nav_names[k])}</a>' for k in slugs if k != key)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": title, "url": url, "inLanguage": lang,
          "itemListElement": [{"@type": "ListItem", "position": i, "name": f"{x['name']} ({x['elo']})"}
                              for i, x in enumerate(d["teams"][:20], 1)]}
    alts = [("en", url_of(key, "en")), ("es", url_of(key, "es")), ("x-default", url_of(key, "en"))]
    css = "../style.css" if lang == "en" else "../../style.css"
    region = t["region"] if key in NATIONS else t["country"]
    return head(lang, full_title, desc, url, alts, css, ld) + f"""<body>
<main>
<p class="eyebrow"><a href="{back}">{t["all"]}</a> · {switch}</p>
<h1 class="title" style="font-size:44px">{e(title)}</h1>
<p>{e(desc)}</p>
<a class="open" href="{open_href}">{t["open"]}</a>
<h2 style="font:700 20px var(--display);margin:6px 0">{t["top"].format(n=min(TOP, n))}</h2>
<table class="seo"><tr><th>#</th><th>{t["name"]}</th><th>{region}</th><th>{t["elo"]}</th><th>{t["matches"]}</th></tr>{rows}</table>
<h2 style="font:700 20px var(--display);margin:22px 0 6px">{t["about_h"]}</h2>
<p>{about}</p>
<h2 style="font:700 20px var(--display);margin:22px 0 6px">{t["how_h"]}</h2>
<p>{how}</p>
<p>{t["all_label"]}: <a href="{back}">{t["home"]}</a> · {nav}</p>
</main>
</body>
</html>
"""


ES_TITLE = "Ranking Elo de fútbol – puntuaciones Elo de clubes y selecciones"
ES_DESC = ("Ranking Elo de fútbol: Mundial, Eurocopa, Copa América, Liga de Naciones, Liga de Campeones, Liga Europa, Liga Conferencia, "
           "Premier League, La Liga, Serie A, Bundesliga y Ligue 1. Una sola escala Elo, todos los partidos desde el principio, actualizado a diario.")


def shell_es(index_html):
    """The Spanish version of the interactive app: the English index.html with Spanish metadata, static texts and
    links, loading the same app.js and data (window.LANG / window.ROOT switch the interface language)."""
    h = index_html
    nav = ('<nav id="seo-links" aria-label="Todos los rankings" style="max-width:960px;margin:0 auto;padding:0 16px 10px;font:400 13px var(--body);color:var(--mute)">Rankings: '
           + " · ".join(f'<a href="rankings/{SLUGS_ES[k]}.html">{e(SHORT_ES[k])}</a>' for k in SLUGS_ES)
           + ' · <a href="../" hreflang="en" lang="en">English</a></nav>')
    subtitle = " · ".join(SHORT_ES[k].split(" (")[0] for k in ("wc", "euro", "copa", "nl", "ucl", "el", "conf", "uefa", "pl", "ekstraklasa", "bundesliga", "spain", "france", "italy"))
    reps = [
        (r'<html lang="en">', '<html lang="es">'),
        (r"<title>.*?</title>", f"<title>{e(ES_TITLE)}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(ES_DESC)}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{BASE}es/">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(ES_TITLE)}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(ES_DESC)}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{BASE}es/">'),
        (r'"inLanguage":"en"', '"inLanguage":"es"'),
        (r'href="style.css"', 'href="../style.css"'),
        (r"url\('img/home.jpg'\)", "url('../img/home.jpg')"),
        (r'<div class="eyebrow">Football</div>', '<div class="eyebrow">Fútbol</div>'),
        (r'(<div class="subtitle">)World Cup[^<]*(</div>)', lambda m: m.group(1) + e(subtitle) + m.group(2)),
        (r"← All rankings", "← Todos los rankings"),
        (r'<nav id="lang".*?</nav>', '<nav id="lang" aria-label="Idioma"><a data-l="en" href="../" hreflang="en" lang="en">EN</a><a data-l="es" href="./" hreflang="es" lang="es">ES</a></nav>'),
        (r'<nav id="seo-links".*?</nav>', lambda m: nav),
        (r"<noscript>.*?</noscript>", "<noscript><p style=\"padding:16px\">Ranking ELO de fútbol: puntuaciones ELO de selecciones y clubes, actualizadas a diario. Se necesita JavaScript para la vista interactiva; las páginas estáticas de arriba muestran la parte alta de cada ranking.</p></noscript>"),
        (r'href="update.html"', 'href="../update.html"'),
        (r'<script src="app.js" defer></script>', '<script>window.LANG = "es"; window.ROOT = "../";</script>\n<script src="../app.js" defer></script>'),
    ]
    for pat, rep in reps:
        h = re.sub(pat, rep, h, count=1, flags=re.S)
    return h


def sitemap():
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [BASE, f"{BASE}es/"] + [url_of(k, lang) for lang in ("en", "es") for k in SLUGS]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{day}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


def generate(site):
    site = Path(site)
    for sub in ("rankings", "es/rankings"):
        (site / sub).mkdir(parents=True, exist_ok=True)
    for key, slug in SLUGS.items():
        f = site / "data" / f"{key}.json"
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            (site / "rankings" / f"{slug}.html").write_text(page(key, d), encoding="utf-8")
            (site / "es" / "rankings" / f"{SLUGS_ES[key]}.html").write_text(page(key, d, "es"), encoding="utf-8")
    index = site / "index.html"
    if index.exists():
        (site / "es" / "index.html").write_text(shell_es(index.read_text(encoding="utf-8")), encoding="utf-8")
    (site / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
