"""Static, crawlable pages for search engines (the site itself is a single-page app with #hash routes,
which Google does not index as separate pages).

Generated into site/ on every build (and git-ignored): one page per ranking with its own title, description
and the top of the table as plain HTML, plus sitemap.xml.
"""
import html
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://enterdesign.github.io/footballelo/"
SLUGS = {"wc": "world-cup", "euro": "european-championship", "copa": "copa-america", "nl": "nations-league",
         "ucl": "champions-league", "el": "europa-league", "conf": "conference-league",
         "uefa": "uefa-club-competitions", "pl": "premier-league", "ekstraklasa": "ekstraklasa"}
NATIONS = {"wc", "euro", "copa", "nl"}
TOP = 50
e = html.escape


def describe(d, key):
    first, last = d["matches"][0][0], d["matches"][-1][0]
    noun = "national teams" if key in NATIONS else "clubs"
    top = ", ".join(f"{t['name']} ({t['elo']})" for t in d["teams"][:3])
    return (f"{d['title']} ELO ranking: ratings of {len(d['teams'])} {noun} from {first} to {last}, "
            f"{len(d['matches']):,} matches rated. Top now: {top}. Updated daily.")


def page(key, d):
    slug = SLUGS[key]
    url = f"{BASE}rankings/{slug}.html"
    desc = describe(d, key)
    title = f"{d['title']} ELO ranking"
    rows = "".join(
        f"<tr><td>{i}</td><td>{e(t['name'])}</td><td>{e(t.get('country') or t.get('label') or '')}</td>"
        f"<td>{t['elo']}</td><td>{t['matches']}</td></tr>" for i, t in enumerate(d["teams"][:TOP], 1))
    ks = ", ".join(f"{e(p['label'])} {p['k']}" for p in d["phases"].values())
    nav = " · ".join(f'<a href="{s}.html">{s.replace("-", " ").title()}</a>' for k_, s in SLUGS.items() if k_ != key)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": title, "url": url,
          "itemListElement": [{"@type": "ListItem", "position": i, "name": f"{t['name']} ({t['elo']})"}
                              for i, t in enumerate(d["teams"][:20], 1)]}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)} – Football ELO</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)} – Football ELO">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="../style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>main{{max-width:960px;margin:0 auto;padding:22px 16px 60px}}table.seo{{width:100%;border-collapse:collapse;font:400 15px var(--body)}}
table.seo th{{text-align:left;font:600 14px var(--display);color:var(--mute);border-bottom:1px solid var(--ink);padding:6px 8px}}
table.seo td{{padding:6px 8px;border-bottom:1px solid var(--rule)}}.open{{display:inline-block;margin:12px 0 18px;padding:8px 16px;background:var(--ink);color:#fff;font:600 16px var(--display)}}</style>
</head>
<body>
<main>
<p class="eyebrow"><a href="../">← All rankings</a></p>
<h1 class="title" style="font-size:44px">{e(title)}</h1>
<p>{e(desc)}</p>
<a class="open" href="../#{key}">Open the interactive ranking</a>
<h2 style="font:700 20px var(--display);margin:6px 0">Top {min(TOP, len(d["teams"]))}</h2>
<table class="seo"><tr><th>#</th><th>Name</th><th>{'Region' if key in NATIONS else 'Country'}</th><th>ELO</th><th>Matches</th></tr>{rows}</table>
<h2 style="font:700 20px var(--display);margin:22px 0 6px">How the rating works</h2>
<p>Every team starts at 1600. After each match R ← R + K × (S − E), where E = 1 / (1 + 10^((R<sub>opponent</sub> − R) / 400)) and S is 1 for a win, 0.5 for a draw, 0 for a loss. A match decided on penalties counts as a win for the shoot-out winner. K-factors by stage: {ks}.</p>
<p>All rankings: <a href="../">home</a> · {nav}</p>
</main>
</body>
</html>
"""


def sitemap():
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [BASE] + [f"{BASE}rankings/{s}.html" for s in SLUGS.values()]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{day}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n'


def generate(site):
    site = Path(site)
    out = site / "rankings"
    out.mkdir(parents=True, exist_ok=True)
    for key, slug in SLUGS.items():
        f = site / "data" / f"{key}.json"
        if f.exists():
            (out / f"{slug}.html").write_text(page(key, json.loads(f.read_text(encoding="utf-8"))), encoding="utf-8")
    (site / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
