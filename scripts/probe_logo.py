#!/usr/bin/env python3
"""One-off: does the crest lookup work for a batch of clubs?"""
import logos

for name in ("Nottingham Forest", "Hamburger SV", "Zenit St. Petersburg", "AIK Stockholm", "APOEL FC",
             "Podbeskidzie Bielsko-Biała", "Polonia Bytom", "Dyskobolia Grodzisk Wielkopolski",
             "Górnik Wałbrzych", "Pogoń Lwów", "Olimpia Poznań", "Union Touring Łódź", "Hapoel Tel Aviv", "Anorthosis"):
    print(f"{name:36} -> {logos.wiki_logo(name)}", flush=True)
