#!/usr/bin/env python3
"""One-off: does the rewritten Wikipedia crest lookup work?"""
import logos

for name in ("Nottingham Forest", "Hamburger SV", "Zenit St. Petersburg", "AIK Stockholm", "APOEL FC",
             "Podbeskidzie Bielsko-Biała", "Polonia Bytom", "Dyskobolia Grodzisk Wielkopolski",
             "Górnik Wałbrzych", "Pogoń Lwów", "Olimpia Poznań", "Union Touring Łódź"):
    print(f"{name:36} -> {logos.wiki_logo(name)}")
