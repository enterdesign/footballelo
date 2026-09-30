#!/usr/bin/env python3
"""One-off: look at how Polish league results are published (structure only)."""
import re
import urllib.request

UA = {"User-Agent": "footballelo-research/1.0 (personal ELO project)"}


def get(url, enc=None):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
        ctype = r.headers.get("Content-Type", "")
    for e in ([enc] if enc else []) + ["utf-8", "cp1250"]:
        try:
            return raw.decode(e), ctype
        except Exception:
            pass
    return raw.decode("latin-1"), ctype


def text(html):
    html = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
    html = re.sub(r"(?i)</(tr|p|div|h\d|li)>|<br\s*/?>", "\n", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = re.sub(r"[ \t\xa0]+", " ", html)
    return re.sub(r"\n\s*\n+", "\n", html)


for url in ("http://www.90minut.pl/liga/1/liga11133.html",
            "http://www.90minut.pl/liga/1/liga12530.html"):
    try:
        html, ctype = get(url)
        print("=====", url, len(html), ctype)
        print("links:", sorted(set(re.findall(r'href="([^"]*liga[^"]*)"', html)))[:25])
        t = text(html)
        print(t[:2500])
    except Exception as e:
        print("ERR", url, e)

for title in ("1978%E2%80%9379_Ekstraklasa", "1927_Ekstraklasa"):
    url = f"https://en.wikipedia.org/w/index.php?title={title}&action=raw"
    try:
        wt, _ = get(url)
        i = wt.find("Results")
        print("=====", url, len(wt))
        print(wt[i:i + 1800])
    except Exception as e:
        print("ERR", url, e)
