"""Static, crawlable pages for search engines (the site itself is a single-page app with #hash routes,
which Google does not index as separate pages).

Generated into site/ on every build (and git-ignored): for every language (English in rankings/, Spanish in es/,
Portuguese in pt/, Polish in pl/) one page per ranking with its own title, description and the top of the table as
plain HTML, plus the language's copy of the interactive app (xx/index.html, made from index.html) and sitemap.xml.
"""
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://enterdesign.github.io/footballelo/"
LANGS = ("en", "es", "pt", "pl")
SLUGS = {"wc": "world-cup", "euro": "european-championship", "copa": "copa-america", "nl": "nations-league",
         "ucl": "champions-league", "el": "europa-league", "conf": "conference-league",
         "uefa": "uefa-club-competitions", "pl": "premier-league", "ekstraklasa": "ekstraklasa", "bundesliga": "bundesliga", "spain": "la-liga", "france": "ligue-1", "italy": "serie-a"}
LEAGUES = {"pl": "premier-league", "ekstraklasa": "ekstraklasa", "bundesliga": "bundesliga", "spain": "la-liga", "france": "ligue-1", "italy": "serie-a"}
SLUGS_BY = {
    "en": SLUGS,
    "es": {"wc": "copa-del-mundo", "euro": "eurocopa", "copa": "copa-america", "nl": "liga-de-naciones", "ucl": "liga-de-campeones",
           "el": "liga-europa", "conf": "liga-conferencia", "uefa": "competiciones-uefa-de-clubes", **LEAGUES},
    "pt": {"wc": "copa-do-mundo", "euro": "eurocopa", "copa": "copa-america", "nl": "liga-das-nacoes", "ucl": "liga-dos-campeoes",
           "el": "liga-europa", "conf": "liga-conferencia", "uefa": "competicoes-de-clubes-da-uefa", **LEAGUES},
    "pl": {"wc": "mistrzostwa-swiata", "euro": "mistrzostwa-europy", "copa": "copa-america", "nl": "liga-narodow", "ucl": "liga-mistrzow",
           "el": "liga-europy", "conf": "liga-konferencji", "uefa": "rozgrywki-klubowe-uefa", **LEAGUES},
}
# names of the rankings in each language (titles, navigation)
SHORT = {
    "es": {"wc": "Mundial de fútbol (Copa del Mundo)", "euro": "Eurocopa", "copa": "Copa América", "nl": "Liga de Naciones",
           "ucl": "Liga de Campeones", "el": "Liga Europa", "conf": "Liga Conferencia", "uefa": "competiciones UEFA de clubes",
           "pl": "Premier League", "ekstraklasa": "Ekstraklasa", "bundesliga": "Bundesliga", "spain": "La Liga", "france": "Ligue 1", "italy": "Serie A"},
    "pt": {"wc": "Copa do Mundo (Mundial)", "euro": "Eurocopa", "copa": "Copa América", "nl": "Liga das Nações",
           "ucl": "Liga dos Campeões", "el": "Liga Europa", "conf": "Liga Conferência", "uefa": "competições de clubes da UEFA",
           "pl": "Premier League", "ekstraklasa": "Ekstraklasa", "bundesliga": "Bundesliga", "spain": "La Liga", "france": "Ligue 1", "italy": "Serie A"},
    "pl": {"wc": "Mistrzostwa świata", "euro": "Mistrzostwa Europy", "copa": "Copa América", "nl": "Liga Narodów",
           "ucl": "Liga Mistrzów", "el": "Liga Europy", "conf": "Liga Konferencji", "uefa": "rozgrywki klubowe UEFA",
           "pl": "Premier League", "ekstraklasa": "Ekstraklasa", "bundesliga": "Bundesliga", "spain": "La Liga", "france": "Ligue 1", "italy": "Serie A"},
}
# English titles of the pages that match what people search for ("elo champions league", "world football elo ratings", ...)
EN_TITLES = {"uefa": "UEFA club ELO ranking: Champions League, Europa League & Conference League",
             "ucl": "Champions League ELO ranking – ELO ratings of every club since {first}",
             "wc": "World football ELO ratings – national team ELO ranking since {first}"}
NATIONS = {"wc", "euro", "copa", "nl"}
TOP = 50
e = html.escape

# Texts of the static pages. {n} teams, {noun}, {first}/{last} seasons, {m} matches, {top} leaders, {ks} K-factors.
TX = {
    "en": {"name": "English", "all": "← All rankings", "open": "Open the interactive ranking", "top": "Top {n}", "col_name": "Name",
           "country": "Country", "region": "Region", "elo": "ELO", "matches": "Matches", "about_h": "About this football ELO ranking",
           "how_h": "How the rating works", "all_label": "All rankings", "home": "home"},
    "es": {"name": "Español", "all": "← Todos los rankings", "open": "Abrir el ranking interactivo", "top": "Top {n}", "col_name": "Nombre",
           "country": "País", "region": "Región", "elo": "Elo", "matches": "Partidos", "about_h": "Sobre este ranking Elo de fútbol",
           "how_h": "Cómo funciona la puntuación", "all_label": "Todos los rankings", "home": "inicio",
           "nouns": ("clubes", "selecciones"), "title": "Ranking Elo – {short}", "full_title": "{title}: clasificación Elo de fútbol desde {first}",
           "desc": "Ranking Elo – {short}: puntuación Elo de {n} {noun} de {first} a {last}, {m} partidos valorados. Líderes actuales: {top}. Actualizado a diario.",
           "about": ("Este es un ranking Elo de fútbol de {n} {noun}, calculado partido a partido de {first} a {last} ({m} partidos). "
                     "Cada equipo tiene una puntuación Elo continua, por lo que los valores se pueden comparar entre temporadas. El ranking se recalcula "
                     "con todo el historial de partidos y se actualiza a diario. En la versión interactiva puedes ver el historial de cada "
                     "equipo, su máxima puntuación histórica, los cambios temporada a temporada, cada partido con la puntuación posterior y comparaciones cara a cara."),
           "how": ("Todos los equipos empiezan con 1600 puntos. Tras cada partido: R ← R + K × (S − E), donde E = 1 / (1 + 10^((R<sub>rival</sub> − R) / 400)) "
                   "y S es 1 por victoria, 0,5 por empate y 0 por derrota. Un partido decidido en penaltis cuenta como victoria para el ganador de la tanda. "
                   "Factores K por fase: {ks}."),
           "shell_title": "Ranking Elo de fútbol – puntuaciones Elo de clubes y selecciones",
           "shell_desc": ("Ranking Elo de fútbol: Mundial, Eurocopa, Copa América, Liga de Naciones, Liga de Campeones, Liga Europa, Liga Conferencia, "
                          "Premier League, La Liga, Serie A, Bundesliga y Ligue 1. Una sola escala Elo, todos los partidos desde el principio, actualizado a diario."),
           "eyebrow": "Fútbol", "aria": "Todos los rankings",
           "noscript": "Ranking ELO de fútbol: puntuaciones ELO de selecciones y clubes, actualizadas a diario. Se necesita JavaScript para la vista interactiva; las páginas estáticas de arriba muestran la parte alta de cada ranking."},
    "pt": {"name": "Português", "all": "← Todos os rankings", "open": "Abrir o ranking interativo", "top": "Top {n}", "col_name": "Nome",
           "country": "País", "region": "Região", "elo": "Elo", "matches": "Jogos", "about_h": "Sobre este ranking Elo de futebol",
           "how_h": "Como funciona a pontuação", "all_label": "Todos os rankings", "home": "início",
           "nouns": ("clubes", "seleções"), "title": "Ranking Elo – {short}", "full_title": "{title}: classificação Elo de futebol desde {first}",
           "desc": "Ranking Elo – {short}: pontuação Elo de {n} {noun} de {first} a {last}, {m} jogos avaliados. Líderes atuais: {top}. Atualizado diariamente.",
           "about": ("Este é um ranking Elo de futebol de {n} {noun}, calculado jogo a jogo de {first} a {last} ({m} jogos). "
                     "Cada equipe tem uma pontuação Elo contínua, por isso os valores podem ser comparados entre temporadas. O ranking é recalculado "
                     "com todo o histórico de jogos e atualizado diariamente. Na versão interativa você vê o histórico de cada equipe, a sua pontuação "
                     "máxima de todos os tempos, as variações temporada a temporada, cada jogo com a pontuação posterior e comparações frente a frente."),
           "how": ("Todas as equipes começam com 1600 pontos. Depois de cada jogo: R ← R + K × (S − E), onde E = 1 / (1 + 10^((R<sub>adversário</sub> − R) / 400)) "
                   "e S é 1 para vitória, 0,5 para empate e 0 para derrota. Um jogo decidido nos pênaltis conta como vitória para o vencedor da disputa. "
                   "Fatores K por fase: {ks}."),
           "shell_title": "Ranking Elo de futebol – pontuações Elo de clubes e seleções",
           "shell_desc": ("Ranking Elo de futebol: Copa do Mundo, Eurocopa, Copa América, Liga das Nações, Liga dos Campeões, Liga Europa, Liga Conferência, "
                          "Premier League, La Liga, Serie A, Bundesliga e Ligue 1. Uma única escala Elo, todos os jogos desde o início, atualizado diariamente."),
           "eyebrow": "Futebol", "aria": "Todos os rankings",
           "noscript": "Ranking ELO de futebol: pontuações ELO de seleções e clubes, atualizadas diariamente. É preciso JavaScript para a vista interativa; as páginas estáticas acima mostram o topo de cada ranking."},
    "pl": {"name": "Polski", "all": "← Wszystkie rankingi", "open": "Otwórz interaktywny ranking", "top": "Top {n}", "col_name": "Nazwa",
           "country": "Kraj", "region": "Region", "elo": "Elo", "matches": "Mecze", "about_h": "O rankingu Elo piłki nożnej",
           "how_h": "Jak działa punktacja", "all_label": "Wszystkie rankingi", "home": "strona główna",
           "nouns": ("klubów", "reprezentacji"), "title": "Ranking Elo – {short}", "full_title": "{title}: punktacja Elo w piłce nożnej od {first}",
           "desc": "Ranking Elo – {short}: punktacja Elo {n} {noun} od {first} do {last}, ocenionych meczów: {m}. Obecni liderzy: {top}. Aktualizowany codziennie.",
           "about": ("To ranking Elo piłki nożnej dla {n} {noun}, liczony mecz po meczu od {first} do {last} ({m} meczów). "
                     "Każdy zespół ma jedną ciągłą punktację Elo, więc wartości można porównywać między sezonami. Ranking jest przeliczany z pełnej "
                     "historii meczów i odświeżany codziennie. W wersji interaktywnej zobaczysz historię punktacji każdego zespołu, jej rekord wszech czasów, "
                     "zmiany sezon po sezonie, każdy mecz z punktacją po nim oraz porównania bezpośrednie."),
           "how": ("Każdy zespół zaczyna z 1600 punktami. Po każdym meczu: R ← R + K × (S − E), gdzie E = 1 / (1 + 10^((R<sub>rywala</sub> − R) / 400)), "
                   "a S wynosi 1 za zwycięstwo, 0,5 za remis i 0 za porażkę. Mecz rozstrzygnięty w rzutach karnych liczy się jako zwycięstwo dla zwycięzcy serii. "
                   "Współczynniki K według fazy: {ks}."),
           "shell_title": "Ranking Elo piłki nożnej – punktacja Elo klubów i reprezentacji",
           "shell_desc": ("Ranking Elo piłki nożnej: mistrzostwa świata, mistrzostwa Europy, Copa América, Liga Narodów, Liga Mistrzów, Liga Europy, Liga Konferencji, "
                          "Premier League, La Liga, Serie A, Bundesliga i Ligue 1. Jedna skala Elo, wszystkie mecze od początku, aktualizacja codziennie."),
           "eyebrow": "Piłka nożna", "aria": "Wszystkie rankingi",
           "noscript": "Ranking ELO piłki nożnej: punktacja ELO reprezentacji i klubów, aktualizowana codziennie. Widok interaktywny wymaga JavaScriptu; statyczne strony powyżej pokazują czołówkę każdego rankingu."},
}


def url_of(key, lang):
    return f"{BASE}rankings/{SLUGS[key]}.html" if lang == "en" else f"{BASE}{lang}/rankings/{SLUGS_BY[lang][key]}.html"


def home_url(lang):
    return BASE if lang == "en" else f"{BASE}{lang}/"


def span(d):
    return d["matches"][0][0], d["matches"][-1][0]


def alternates(key=None):
    """hreflang links of a page: every language version plus x-default (English)."""
    u = (lambda l: url_of(key, l)) if key else home_url
    return [(l, u(l)) for l in LANGS] + [("x-default", u("en"))]


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
    first, last = span(d)
    n, m = len(d["teams"]), f"{len(d['matches']):,}"
    ks = ", ".join(f"{e(p['label'])} {p['k']}" for p in d["phases"].values())
    if lang == "en":
        desc = describe(d, key)
        title = f"{d['title']} ELO ranking"
        full_title = EN_TITLES[key].format(first=first) if key in EN_TITLES else f"{title} – football ELO ratings since {first}"
        noun = "national teams" if key in NATIONS else "clubs"
        nav_names = {k: s.replace("-", " ").title() for k, s in SLUGS.items()}
        about = (f"This is a football ELO ranking of {n} {noun}, rated match by match from {e(first)} to {e(last)} ({m} matches). "
                 "Every team has one continuous ELO rating, so the numbers can be compared across seasons. The ranking is rebuilt from the full "
                 "match history and refreshed daily. In the interactive version you can see the rating history of each team, its all-time high "
                 "rating, season-by-season changes, every match with the rating after it, and head-to-head comparisons.")
        how = ("Every team starts at 1600. After each match R ← R + K × (S − E), where E = 1 / (1 + 10^((R<sub>opponent</sub> − R) / 400)) and S is 1 "
               "for a win, 0.5 for a draw, 0 for a loss. A match decided on penalties counts as a win for the shoot-out winner. "
               f"K-factors by stage: {ks}.")
        open_href, css = f"../#{key}", "../style.css"
    else:
        short = SHORT[lang][key]
        noun = t["nouns"][1 if key in NATIONS else 0]
        title = t["title"].format(short=short)
        full_title = t["full_title"].format(title=title, first=first)
        top = ", ".join(f"{x['name']} ({x['elo']})" for x in d["teams"][:3])
        desc = t["desc"].format(short=short, n=n, noun=noun, first=first, last=last, m=m, top=top)
        nav_names = SHORT[lang]
        about = t["about"].format(n=n, noun=noun, first=e(first), last=e(last), m=m)
        how = t["how"].format(ks=ks)
        open_href, css = f"../#{key}", "../../style.css"       # the app of that language is es/index.html etc.
    slugs = SLUGS_BY[lang]
    switch = " · ".join(f'<a href="{url_of(key, l)}" hreflang="{l}" lang="{l}">{TX[l]["name"]}</a>' for l in LANGS if l != lang)
    rows = "".join(
        f"<tr><td>{i}</td><td>{e(x['name'])}</td><td>{e(x.get('country') or x.get('label') or '')}</td>"
        f"<td>{x['elo']}</td><td>{x['matches']}</td></tr>" for i, x in enumerate(d["teams"][:TOP], 1))
    nav = " · ".join(f'<a href="{slugs[k]}.html">{e(nav_names[k])}</a>' for k in slugs if k != key)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": title, "url": url, "inLanguage": lang,
          "itemListElement": [{"@type": "ListItem", "position": i, "name": f"{x['name']} ({x['elo']})"}
                              for i, x in enumerate(d["teams"][:20], 1)]}
    region = t["region"] if key in NATIONS else t["country"]
    return head(lang, full_title, desc, url, alternates(key), css, ld) + f"""<body>
<main>
<p class="eyebrow"><a href="../">{t["all"]}</a> · {switch}</p>
<h1 class="title" style="font-size:44px">{e(title)}</h1>
<p>{e(desc)}</p>
<a class="open" href="{open_href}">{t["open"]}</a>
<h2 style="font:700 20px var(--display);margin:6px 0">{t["top"].format(n=min(TOP, n))}</h2>
<table class="seo"><tr><th>#</th><th>{t["col_name"]}</th><th>{region}</th><th>{t["elo"]}</th><th>{t["matches"]}</th></tr>{rows}</table>
<h2 style="font:700 20px var(--display);margin:22px 0 6px">{t["about_h"]}</h2>
<p>{about}</p>
<h2 style="font:700 20px var(--display);margin:22px 0 6px">{t["how_h"]}</h2>
<p>{how}</p>
<p>{t["all_label"]}: <a href="../">{t["home"]}</a> · {nav}</p>
</main>
</body>
</html>
"""


def lang_nav(lang):
    """The EN | ES | PT | PL switch as plain links (app.js keeps the current route in them)."""
    up = "" if lang == "en" else "../"
    links = "".join(
        f'<a data-l="{l}" href="{"./" if l == lang else up + ("" if l == "en" else l + "/")}" hreflang="{l}" lang="{l}">{l.upper()}</a>' for l in LANGS)
    return f'<nav id="lang" aria-label="Language">{links}</nav>'


def shell(index_html, lang):
    """The copy of the interactive app for one language: the English index.html with translated metadata, static texts
    and links, loading the same app.js, i18n.js and data (window.LANG / window.ROOT select the interface language)."""
    t = TX[lang]
    h = index_html
    others = " · ".join(f'<a href="{"../" if l == "en" else "../" + l + "/"}" hreflang="{l}" lang="{l}">{TX[l]["name"]}</a>' for l in LANGS if l != lang)
    nav = (f'<nav id="seo-links" aria-label="{e(t["aria"])}" style="max-width:960px;margin:0 auto;padding:0 16px 10px;font:400 13px var(--body);color:var(--mute)">Rankings: '
           + " · ".join(f'<a href="rankings/{SLUGS_BY[lang][k]}.html">{e(SHORT[lang][k])}</a>' for k in SLUGS_BY[lang]) + f" · {others}</nav>")
    subtitle = " · ".join(SHORT[lang][k].split(" (")[0] for k in ("wc", "euro", "copa", "nl", "ucl", "el", "conf", "uefa", "pl", "ekstraklasa", "bundesliga", "spain", "france", "italy"))
    reps = [
        (r'<html lang="en">', f'<html lang="{lang}">'),
        (r"<title>.*?</title>", f"<title>{e(t['shell_title'])}</title>"),
        (r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(t["shell_desc"])}">'),
        (r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{home_url(lang)}">'),
        (r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(t["shell_title"])}">'),
        (r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(t["shell_desc"])}">'),
        (r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{home_url(lang)}">'),
        (r'"inLanguage":"en"', f'"inLanguage":"{lang}"'),
        (r'href="style.css"', 'href="../style.css"'),
        (r"url\('img/home.jpg'\)", "url('../img/home.jpg')"),
        (r'<div class="eyebrow">Football</div>', f'<div class="eyebrow">{e(t["eyebrow"])}</div>'),
        (r'(<div class="subtitle">)World Cup[^<]*(</div>)', lambda m: m.group(1) + e(subtitle) + m.group(2)),
        (r"← All rankings", t["all"]),
        (r'<nav id="lang".*?</nav>', lambda m: lang_nav(lang)),
        (r'<nav id="seo-links".*?</nav>', lambda m: nav),
        (r"<noscript>.*?</noscript>", lambda m: f'<noscript><p style="padding:16px">{e(t["noscript"])}</p></noscript>'),
        (r'href="update.html"', 'href="../update.html"'),
        (r'<script src="i18n.js" defer></script>', '<script src="../i18n.js" defer></script>'),
        (r'<script src="app.js" defer></script>', lambda m: f'<script>window.LANG = "{lang}"; window.ROOT = "../";</script>\n<script src="../app.js" defer></script>'),
    ]
    for pat, rep in reps:
        h = re.sub(pat, rep, h, count=1, flags=re.S)
    return h


def sitemap():
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [home_url(l) for l in LANGS] + [url_of(k, l) for l in LANGS for k in SLUGS]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{day}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


def generate(site):
    site = Path(site)
    for l in LANGS:
        (site / ("rankings" if l == "en" else f"{l}/rankings")).mkdir(parents=True, exist_ok=True)
    for key in SLUGS:
        f = site / "data" / f"{key}.json"
        if f.exists():
            d = json.loads(f.read_text(encoding="utf-8"))
            for l in LANGS:
                out = site / "rankings" if l == "en" else site / l / "rankings"
                (out / f"{SLUGS_BY[l][key]}.html").write_text(page(key, d, l), encoding="utf-8")
    index = site / "index.html"
    if index.exists():
        for l in LANGS[1:]:
            (site / l / "index.html").write_text(shell(index.read_text(encoding="utf-8"), l), encoding="utf-8")
    (site / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
