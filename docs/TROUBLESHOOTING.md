# Co robić, gdy coś nie działa

Wszystko poniżej da się zrobić w przeglądarce na GitHubie (ołówek ✏️ przy pliku → **Commit changes** → bezpośrednio na `main`).
Każdy commit na `main` sam uruchamia przebieg „Update & deploy”; strona jest gotowa po 2–5 minutach.

## Jak to działa (w skrócie)

```
codziennie 05:17 UTC  →  sync.py (pobiera nowe mecze)  →  build.py (liczy ELO od zera)  →  strona (GitHub Pages)
                              │                                │
                              │                                └─ nieznana nazwa drużyny → issue „Unknown team names…”
                              └─ źródło nie dostarcza meczów od 3 tygodni → issue „No new matches from some sources”
```

- Dane (`data/matches/*.json`) są zapisywane w repozytorium, więc strona zawsze ma ostatnią dobrą wersję.
- Rankingi są liczone **od zera** przy każdym przebiegu, więc poprawka w danych lub w nazwach działa wstecz.
- Przebieg można uruchomić ręcznie: **Actions → Update & deploy → Run workflow**.

## Gdzie szukać informacji

| Co widzisz | Gdzie zajrzeć |
|---|---|
| Nowy issue w repozytorium | zakładka **Issues** – treść mówi, co poprawić |
| Czerwony ✗ przy przebiegu | **Actions → Update & deploy → ostatni przebieg → job „build” → rozwiń czerwony krok** |
| Strona pokazuje stare dane | patrz „Strona pokazuje stare dane” poniżej |
| Nie wiesz, czy automat działa | na stronie głównej: „Last data check” (ma pokazywać dzisiejszą datę) |

---

## 1. Unknown team names (nieznane nazwy drużyn)

**Objaw:** issue „Unknown team names in daily update”, a w jego treści np.

```
[el] 2 unknown team name(s) — add them (or as an alias) in data/teams_el.json:
    Nowy Klub FC
    FC Nowy Klub II
```

Przebieg zatrzymuje się, dopóki nie zdecydujesz, co to za drużyna (strona zostaje na ostatniej dobrej wersji).
Plik do edycji jest w nawiasie: `data/teams_<rozgrywki>.json` (`ucl`, `el`, `conf`, `pl`, `ekstraklasa`, `wc`, `euro`, `copa`, `nl`).

**a) To nowy klub / reprezentacja** – dopisz wpis na końcu (przed ostatnim `}`, pamiętaj o przecinku po poprzednim):

```json
"Nowy Klub": {"aliases": ["Nowy Klub FC"], "country": "Poland", "code": "POL"}
```

- kluby: `country` (po angielsku) i `code` (3 litery, jak u sąsiednich klubów tego kraju); `logo` jest opcjonalne (bez niego pokaże się monogram),
- reprezentacje (`teams_wc.json`, `_euro`, `_copa`, `_nl`): zamiast `logo` jest `iso` – kod flagi z flagcdn.com, np. `"iso": "pl"`, `"gb-eng"`.

**b) To ten sam klub pod inną nazwą (zmiana nazwy, inna pisownia)** – nie dodawaj nowego wpisu, tylko dopisz nazwę do `aliases` istniejącego:

```json
"Dinamo Zagreb": {"aliases": ["Croatia Zagreb", "GNK Dinamo Zagreb"], "country": "Croatia", "code": "CRO"}
```

**c) Państwo lub klub się połączył/rozpadł** – następca dziedziczy historię przez `aliases`, a krótki opis idzie w `note`:

```json
"Serbia": {"note": "Includes Yugoslavia and Serbia & Montenegro", "iso": "rs", "aliases": ["Yugoslavia", "Serbia and Montenegro"]}
```

**d) Błąd „alias 'X' is claimed by both 'A' and 'B'”** – ta sama nazwa jest wpisana w dwóch klubach. Usuń ją z jednego z nich
(albo połącz oba kluby w jeden wpis, jeśli to naprawdę ten sam klub).

**e) Ten sam klub widać na stronie dwa razy** (np. „Seville” i „Sevilla”, „Rostov” i „Rostov-on-Don”) – nazwa wpadła do bazy pod dwoma
wpisami. W pliku, w którym są oba, usuń wpis z gorszą nazwą i dopisz ją do `aliases` tego dobrego:

```json
"Sevilla": {"aliases": ["Sevilla FC", "Seville"], "country": "Spain", "code": "ESP"}
```

Jeśli kluby są w różnych plikach (np. `teams_ucl.json` ma „Aalborg”, a `teams_el.json` „AaB”), ujednolić nazwę w obu –
wspólny ranking UEFA łączy kluby po nazwie i kraju, więc nazwy muszą być takie same (pisownia z Ligi Mistrzów ma pierwszeństwo).
Gdy to naprawdę dwa różne kluby, a nie dwie pisownie (np. Cercle Brugge i Club Brugge), nic nie łącz.

Po commicie przebieg uruchomi się sam. Issue możesz zamknąć.

> Wspólny ranking UEFA (`uefa`) nie ma własnego pliku: łączy `teams_ucl`, `teams_el` i `teams_conf` automatycznie po nazwie i kraju.
> Jeśli jeden klub pojawia się w nim dwa razy (np. „Sparta” i „Sparta Praga”), ujednolić nazwę w `teams_el.json` / `teams_conf.json`
> tak, żeby była taka sama jak w `teams_ucl.json`.

---

## 2. „No new matches from some sources” (cicha awaria źródła)

**Objaw:** issue „No new matches from some sources”, np.

```
Europa League: no new matches for 34 days (last change 2026-10-02)
```

Alarm włącza się tylko w miesiącach, w których dane powinny płynąć co tydzień (np. Liga Mistrzów w X–XI i III–V), więc przerwy letnie i zimowe go nie wywołują.
Bez alarmu strona nadal pokazywałaby świeżą datę „Last data check”, ale stare wyniki.

**Krok 1 – czy to w ogóle problem?** Czasem po prostu nie było meczów (przerwa reprezentacyjna, zawieszenie ligi, pandemia).
Sprawdź w internecie, czy w ostatnich tygodniach rozegrano mecze tych rozgrywek. Jeśli nie – zamknij issue.

**Krok 2 – zajrzyj w logi.** Actions → ostatni „Update & deploy” → krok **Fetch new matches**. Typowe linie:

| Linia w logu | Znaczenie | Co zrobić |
|---|---|---|
| `Wikipedia page '2026–27 UEFA Europa League league phase' failed: HTTP Error 429` | Wikipedia chwilowo ogranicza zapytania | nic; spróbuj ponownie później (Run workflow) |
| `el 2026/27: no matches parsed (stored 24); kept stored` (albo `… fresh copy has fewer matches …`) | pobrano stronę, ale parser nie znalazł meczów → **zmienił się układ strony** | krok 3 |
| `international_results failed (…)` | repozytorium z wynikami reprezentacji niedostępne | poczekaj; dane zostają jak były |
| `football-data.org CL failed (…)` | klucz/limit API | sekcja 8 |
| brak jakichkolwiek komunikatów, a nowych meczów nie ma | źródło nie ma jeszcze tych meczów (np. opóźnienie) | poczekaj kilka dni |

**Krok 3 – zmienił się format źródła.** Parsery są małe i mają testy, więc poprawka to zwykle kilka linii.
Najprościej poprosić Claude Code (kopiuj-wklej):

> Alarm „No new matches” dla Europa League. W logu kroku „Fetch new matches” jest „no matches parsed (stored 24); kept stored”.
> Sprawdź, jak wygląda teraz strona „2026–27 UEFA Europa League league phase” na Wikipedii i popraw `scripts/uefa_wikipedia.py`
> tak, żeby znowu wczytywał mecze. Dodaj test z fragmentem nowego HTML-a.

Gdzie jest który parser:

| Rozgrywki | Źródło | Plik z parserem |
|---|---|---|
| Liga Mistrzów (od 2011/12), Premier League (od 1992/93), World Cup | openfootball (pliki tekstowe) | `scripts/openfootball.py`, `scripts/england.py` |
| bieżący sezon Ligi Mistrzów i Premier League | football-data.org (API) | `scripts/footballdata.py` |
| Liga Narodów, Euro, Copa América | `martj42/international_results` (CSV) | `scripts/nationsleague.py`, `scripts/tournaments.py` |
| bieżąca edycja Ligi Narodów | Wikipedia | `scripts/nl_wikipedia.py` |
| Liga Europy, Liga Konferencji | Wikipedia | `scripts/uefa_wikipedia.py`, `scripts/import_uefa.py` |
| Ekstraklasa | Wikipedia | `scripts/wikipedia_pl.py`, `scripts/import_ekstraklasa.py` |

**Do czasu naprawy** brakujące mecze możesz dopisać ręcznie (sekcja 4) – strona od razu je uwzględni.

---

## 3. Czerwony przebieg (build / testy)

Otwórz czerwony krok i przeczytaj ostatnie linie. Najczęstsze przypadki:

**Błąd składni JSON po Twojej edycji**

```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 42 column 3 (char 1830)
```

Zwykle brakuje przecinka między wpisami albo cudzysłowu. Wróć do edycji pliku, popraw wskazaną linię (±1) i zapisz.
Strona do tego czasu działa na ostatniej dobrej wersji.

**„unknown phase 'xyz' in …”** – w danych jest faza, której nie ma w `data/phases.json`. Dopisz ją (z `label`, `k`, `color`) albo popraw dane.

**Nieudany test** (`FAIL: test_…`) – testy pilnują m.in. liczby meczów w turniejach. Jeśli zawiodły po zmianie danych,
sprawdź, czy zmiana jest zamierzona; jeśli tak, popraw oczekiwaną wartość w `tests/`. W razie wątpliwości użyj promptu:

> Przebieg „Update & deploy” jest czerwony. Odczytaj log ostatniego przebiegu na `main`, znajdź przyczynę i napraw ją.

**Cofnięcie zmiany, która coś zepsuła:** Commits → klikasz zły commit → **Revert** (przycisk „…”) → utwórz PR / commit. Dane i strona wrócą do poprzedniego stanu.

---

## 4. Brakujący lub błędny mecz

Plik `data/overrides.json` pozwala dodać lub usunąć mecze **bez dotykania źródeł**. Struktura:

```json
{
  "ucl": {
    "add": [
      {"season": "2026/27", "phase": "group", "teamA": "Arsenal", "goalsA": 2, "teamB": "Napoli", "goalsB": 1}
    ],
    "remove": [
      {"season": "2026/27", "teamA": "Arsenal", "teamB": "Napoli"}
    ]
  }
}
```

- klucz najwyższego poziomu to rozgrywki: `ucl`, `wc`, `pl`, `ekstraklasa`, `nl`, `euro`, `copa`, `el`, `conf`,
- `remove` przyjmuje dowolny zestaw pól, który jednoznacznie wskazuje mecz (np. sezon + obie drużyny),
- dla World Cup / Euro / Copa zamiast `season` jest `"year"` (np. `"year": "2028"`), a faza to `group`, `r16`, `qf`, `sf`, `3rd`, `final`,
- rzuty karne: dodaj `"penA": 4, "penB": 3` (zwycięzca karnych liczy się jak zwycięzca meczu),
- po dogrywce wpisz wynik po dogrywce i dodaj `"et": true`,
- nazwy drużyn mogą być **dowolnym aliasem** z pliku `teams_*.json`,
- Liga Narodów: w przeróbkach używaj już gotowych pól `season` i `phase` (`A`, `B`, `C`, `D`, `qf`, `sf`, `3rd`, `final`, `poAB`…),
  bo nadpisania stosowane są po przygotowaniu meczów.

Jeśli `remove` niczego nie znajdzie, w logu pojawi się `warning: override 'remove' matched nothing` – sprawdź pisownię pól.

Szybki dostęp: na stronie głównej w prawym dolnym rogu są niewidoczne trzy kropki (`···`) – prowadzą do edycji tego pliku.

---

## 5. Strona pokazuje stare dane

1. Odśwież twardo: **Ctrl+F5** (telefon: otwórz w trybie prywatnym).
2. Sprawdź na stronie głównej „site built” – jeśli to wczorajsza data, zobacz Actions: być może przebieg się nie skończył albo jest w kolejce
   (wdrożenia ustawiają się w kolejce, każde trwa 2–5 minut).
3. Jeśli przebieg jest zielony, a dane stare, to źródło nie dostarcza nowych meczów – patrz sekcja 2.

---

## 6. Zły herb, flaga albo nazwa

- **Herb klubu:** w `data/teams_<rozgrywki>.json` wklej własny adres obrazka w pole `logo` (skrypt nigdy nie nadpisuje ręcznie wpisanego loga).
  Brakujące herby uzupełnia ręczny workflow **Actions → Fetch club logos → Run workflow**.
- **Flaga:** pole `iso` w `teams_wc.json` / `teams_nl.json` / `teams_euro.json` / `teams_copa.json` (np. `"gb-sct"` dla Szkocji).
- **Wyświetlana nazwa:** klucz wpisu w `teams_*.json` to nazwa na stronie. Zmiana klucza zmienia nazwę wszędzie
  (stara nazwa powinna trafić do `aliases`, żeby źródła nadal ją rozpoznawały).

---

## 7. Liga Narodów, Euro, Copa América – zmiany formatu

**Liga Narodów – nowa edycja** (np. 2028/29): nic nie trzeba robić, edycja jest wykrywana automatycznie, a dywizje liczone z awansów i spadków.
Na początku, gdy grupy są niepełne, podział jest tymczasowy i poprawia się sam po fazie grupowej.

**Liga Narodów – zła dywizja w zakończonej edycji:** dopisz ją ręcznie w `data/nl_leagues.json`:

```json
"2026/27": {"from": "2026-09-01", "to": "2028-04-30",
            "divisions": {"A": ["Portugal", "Spain", "…"], "B": ["…"], "C": ["…"], "D": ["…"]}}
```

**Euro / Copa – inny format niż poprzednio** (np. inna liczba meczów grupowych): w `scripts/tournaments.py` zmień funkcje `euro_stages` /
`copa_stages` albo słownik `COPA_GROUP_MATCHES` (liczba meczów grupowych danej edycji). Prompt:

> Copa América 2028 ma inny format (… grup po … drużyn). Dostosuj `scripts/tournaments.py` i dodaj test.

Objaw złego formatu: w historii mecz fazy grupowej ma znaczek „QF” albo odwrotnie.

---

## 8. Klucz do football-data.org

Używany tylko dla bieżącego sezonu Ligi Mistrzów i Premier League.

- Klucz to sekret repozytorium **FOOTBALL_DATA_KEY** (Settings → Secrets and variables → Actions).
- W logu `football-data.org CL failed (HTTP Error 403…)` oznacza zły klucz lub brak uprawnień, `429` – limit zapytań (przejdzie sam).
- Gdy klucza brak lub nie działa, system zostawia ostatnio zapisany sezon i polega na openfootball, który nadrabia z opóźnieniem tygodni.

---

## 9. Automat się nie uruchamia

Harmonogram GitHuba (cron) wyłącza się po 60 dniach bez aktywności w repozytorium. Tutaj codzienny commit (`Daily update: new matches`) temu zapobiega,
ale jeśli w Actions widzisz komunikat „This scheduled workflow is disabled”, wejdź w **Actions → Update & deploy → Enable workflow**.
Uruchomienie bywa opóźnione o kilkanaście minut względem 05:17 UTC – to normalne. Zdarza się też, że GitHub pomija poranny przebieg; dlatego jest drugi, awaryjny harmonogram o 11:17 UTC, który uruchamia się tylko wtedy, gdy dziś rano nie było przebiegu (job „gate” w `update.yml` sprawdza datę w `data/sync.json`).

---

## 10. Lista „Recently added matches” na stronie głównej

Na dole strony głównej jest rozwijana lista meczów, które każdy przebieg dodał w porównaniu z poprzednim (ostatnie 30 dni, najwyżej 400 meczów).
Dane: `data/recent.json` (to, co widać) i `data/build_state.json` (zapamiętany stan do porównania; nie edytuj go ręcznie).

- **Lista jest pusta („No new matches were found in the last updates”)** – nic nowego nie przyszło albo to pierwszy przebieg po wdrożeniu funkcji
  (pierwszy zapisuje tylko stan wyjściowy, żeby nie uznać wszystkich meczów za nowe).
- **Na liście pojawił się cały sezon naraz** – źródło poprawiło lub przeniosło wyniki (np. Wikipedia zmieniła wynik), więc mecze wyglądają na nowe. To tylko informacja, rankingi są liczone poprawnie.
- **Chcesz wyczyścić listę:** w `data/recent.json` wpisz `{"batches":[]}` (commit na `main`).
- Zapis dzieje się tylko w przebiegach planowych i ręcznych (te, które commitują dane), a nie w przebiegach po zmianie plików w repozytorium.

---

## 11. Co w razie wątpliwości

Opisz problem w Claude Code razem z linkiem do czerwonego przebiegu lub issue – wszystkie skrypty mają testy
(`python -m unittest discover -s tests`), więc poprawki da się sprawdzić przed wdrożeniem.
Przykład: „Zobacz issue „No new matches from some sources” i napraw źródło”.
