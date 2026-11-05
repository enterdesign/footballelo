"use strict";
// Two languages share this file and the data: the English page (index.html) and the Spanish page (es/index.html),
// which sets window.LANG = "es" and window.ROOT = "../" before loading it. L(en, es) picks the text.
const LANG = window.LANG === "es" ? "es" : "en";
const ROOT = window.ROOT || "";
const L = (en, es) => (LANG === "es" ? es : en);
const REPO = "https://github.com/enterdesign/footballelo";
const lnk = (href, text) => `<a href="${href}" style="color:var(--accent);text-decoration:underline">${text}</a>`;
const INTL = lnk("https://github.com/martj42/international_results", "international_results");
const WIKI_LINK = lnk("https://en.wikipedia.org", L("English Wikipedia", "Wikipedia en inglés"));
const WIKI = `${WIKI_LINK} (CC BY-SA)`;
const WIKI_OPENFOOTBALL = `${lnk("https://github.com/openfootball", "openfootball")}, football-data.org ${L("and", "y")} ${WIKI_LINK}`;
const COMPS = {
  ucl: {file: "data/ucl.json", c1: "#0b1d4d", c2: "#2147a8", img: "img/ucl.jpg", eyebrow: "UEFA Champions League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "1992/93"},
  el:  {file: "data/el.json", c1: "#c2410c", c2: "#7c2d12", img: "img/home.jpg", eyebrow: "UEFA Europa League (2009/10 →)", short: "Europa League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "2009/10", source: WIKI,
        note: "Since the competition was renamed in 2009/10; the earlier UEFA Cup and Cup Winners' Cup are not included. Qualifying rounds are not rated."},
  conf: {file: "data/conf.json", c1: "#15803d", c2: "#14532d", img: "img/home.jpg", eyebrow: "UEFA Conference League (2021/22 →)", short: "Conference League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "2021/22", source: WIKI, note: "Qualifying rounds are not rated."},
  uefa: {file: "data/uefa.json", c1: "#1e293b", c2: "#475569", img: "img/ucl.jpg", eyebrow: "UEFA Club Competitions", short: "UEFA Club Competitions", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "1992/93", source: WIKI_OPENFOOTBALL,
        note: "One rating per club across the Champions League (1992/93 →), Europa League (2009/10 →) and Conference League (2021/22 →). Every match is rated with the K-factor of its own competition and stage (see K-factors); within a season matches are ordered by stage, then competition. Because opponents carry their results from all three competitions, a club's rating here can differ by a few points from its rating in a single competition's ranking, even if it only ever played in that one (for example Real Madrid in the Champions League)."},
  wc:  {file: "data/wc.json", c1: "#92400e", c2: "#ca8a04", img: "img/wc.jpg", eyebrow: "FIFA World Cup", noun: "Nations", period: "Editions",
        group: t => t.region, groupLabel: t => t.label, first: "1930", flags: true},
  pl:  {file: "data/pl.json", c1: "#3d195b", c2: "#7c3aed", flag: "gb-eng", img: "img/home.jpg", eyebrow: "Premier League (First Division 1888–1992)", short: "Premier League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "England", sub: "England", first: "1888/89", domestic: true},
  ekstraklasa: {file: "data/ekstraklasa.json", c1: "#9f1239", c2: "#e11d48", flag: "pl", img: "img/home.jpg", eyebrow: "Ekstraklasa (I liga 1927–2008)", short: "Ekstraklasa", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "Poland", sub: "Poland", first: "1927", domestic: true},
  bundesliga: {file: "data/bundesliga.json", c1: "#7f1d1d", c2: "#dc2626", flag: "de", img: "img/home.jpg", eyebrow: "Bundesliga (1963 →)", short: "Bundesliga", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "Germany", sub: "Germany", first: "1963/64", domestic: true,
        note: "The Bundesliga started in 1963/64. After German reunification the clubs from the former East Germany simply start at 1600 when they first appear; there is no separate treatment of that period."},
  spain: {file: "data/spain.json", c1: "#92400e", c2: "#f59e0b", flag: "es", img: "img/home.jpg", eyebrow: "La Liga (1928/29 →)", short: "La Liga", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "Spain", sub: "Spain", first: "1928/29", domestic: true,
        note: "No league was played in 1936–39 (Spanish Civil War). The 1986/87 promotion/relegation group stage is not rated. One 1979/80 match (Málaga–Salamanca) is missing from every source."},
  france: {file: "data/france.json", c1: "#1e3a8a", c2: "#3b82f6", flag: "fr", img: "img/home.jpg", eyebrow: "Ligue 1 (Division 1 1932/33 →)", short: "Ligue 1", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "France", sub: "France", first: "1932/33", domestic: true,
        note: "No league was played in 1939–45 (Second World War). The 2019/20 season was stopped in March with 279 of 380 matches played."},
  italy: {file: "data/italy.json", c1: "#166534", c2: "#22c55e", flag: "it", img: "img/home.jpg", eyebrow: "Serie A (1929/30 →)", short: "Serie A", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "Italy", sub: "Italy", first: "1929/30", domestic: true,
        note: "Starts with the first single-table season, 1929/30. No league was played in 1943–45 (war) and 1945/46 (played in two regional groups) is not included. 40 of the 420 matches of 1947/48 are missing from every source."},
  euro: {file: "data/euro.json", c1: "#1e3a8a", c2: "#2563eb", img: "img/home.jpg", eyebrow: "UEFA European Championship", short: "European Championship", noun: "Nations", period: "Editions",
        group: () => "", groupLabel: () => "Europe", sub: "Europe", first: "1960", flags: true, source: INTL},
  copa: {file: "data/copa.json", c1: "#0e7490", c2: "#facc15", img: "img/home.jpg", eyebrow: "Copa América (1993 →)", short: "Copa América", noun: "Nations", period: "Editions",
        group: t => t.region, groupLabel: t => t.label, first: "1993", flags: true, source: INTL,
        note: "Only editions from 1993 are included: since then the tournament has a stable format (groups, quarter-finals, semi-finals, 3rd place, final). Earlier editions were round-robin leagues with changing formats and incomplete records."},
  nl:  {file: "data/nl.json", c1: "#312e81", c2: "#4f46e5", img: "img/home.jpg", eyebrow: "UEFA Nations League", noun: "Nations", period: "Editions", live: "updated daily",
        group: t => t.division, groupLabel: t => `Division ${t.division}`, first: "2018/19", flags: true,
        source: INTL},
};
const COUNTRY_ES = {"Albania": "Albania", "Algeria": "Argelia", "Andorra": "Andorra", "Angola": "Angola", "Argentina": "Argentina", "Armenia": "Armenia", "Australia": "Australia", "Austria": "Austria", "Azerbaijan": "Azerbaiyán", "Belarus": "Bielorrusia", "Belgium": "Bélgica", "Bolivia": "Bolivia", "Bosnia and Herzegovina": "Bosnia y Herzegovina", "Brazil": "Brasil", "Bulgaria": "Bulgaria", "Cameroon": "Camerún", "Canada": "Canadá", "Cape Verde": "Cabo Verde", "Chile": "Chile", "China": "China", "Colombia": "Colombia", "Costa Rica": "Costa Rica", "Croatia": "Croacia", "Cuba": "Cuba", "Curaçao": "Curazao", "Cyprus": "Chipre", "Czechia": "Chequia", "DR Congo": "RD del Congo", "Denmark": "Dinamarca", "East Germany": "Alemania Oriental", "Ecuador": "Ecuador", "Egypt": "Egipto", "El Salvador": "El Salvador", "England": "Inglaterra", "Estonia": "Estonia", "Faroe Islands": "Islas Feroe", "Finland": "Finlandia", "France": "Francia", "Georgia": "Georgia", "Germany": "Alemania", "Ghana": "Ghana", "Gibraltar": "Gibraltar", "Greece": "Grecia", "Haiti": "Haití", "Honduras": "Honduras", "Hungary": "Hungría", "Iceland": "Islandia", "Indonesia": "Indonesia", "Iran": "Irán", "Iraq": "Irak", "Israel": "Israel", "Italy": "Italia", "Ivory Coast": "Costa de Marfil", "Jamaica": "Jamaica", "Japan": "Japón", "Jordan": "Jordania", "Kazakhstan": "Kazajistán", "Kosovo": "Kosovo", "Kuwait": "Kuwait", "Latvia": "Letonia", "Liechtenstein": "Liechtenstein", "Lithuania": "Lituania", "Luxembourg": "Luxemburgo", "Malta": "Malta", "Mexico": "México", "Moldova": "Moldavia", "Montenegro": "Montenegro", "Morocco": "Marruecos", "Netherlands": "Países Bajos", "New Zealand": "Nueva Zelanda", "Nigeria": "Nigeria", "North Korea": "Corea del Norte", "North Macedonia": "Macedonia del Norte", "Northern Ireland": "Irlanda del Norte", "Norway": "Noruega", "Panama": "Panamá", "Paraguay": "Paraguay", "Peru": "Perú", "Poland": "Polonia", "Portugal": "Portugal", "Qatar": "Catar", "Republic of Ireland": "República de Irlanda", "Romania": "Rumanía", "Russia": "Rusia", "San Marino": "San Marino", "Saudi Arabia": "Arabia Saudita", "Scotland": "Escocia", "Senegal": "Senegal", "Serbia": "Serbia", "Slovakia": "Eslovaquia", "Slovenia": "Eslovenia", "South Africa": "Sudáfrica", "South Korea": "Corea del Sur", "Spain": "España", "Sweden": "Suecia", "Switzerland": "Suiza", "Togo": "Togo", "Trinidad and Tobago": "Trinidad y Tobago", "Tunisia": "Túnez", "Turkey": "Turquía", "Ukraine": "Ucrania", "United Arab Emirates": "Emiratos Árabes Unidos", "United States": "Estados Unidos", "Uruguay": "Uruguay", "Uzbekistan": "Uzbekistán", "Venezuela": "Venezuela", "Wales": "Gales"};
const REGION_ES = {"Africa": "África", "Asia": "Asia", "Europe": "Europa", "N/C America & Caribbean": "Norte y Centroamérica y Caribe", "Oceania": "Oceanía", "South America": "Sudamérica"};
const COMPS_ES = {
  ucl: {eyebrow: "Liga de Campeones de la UEFA", short: "Liga de Campeones"},
  el: {eyebrow: "Liga Europa de la UEFA (2009/10 →)", short: "Liga Europa",
       note: "Desde que la competición cambió de nombre en 2009/10; no se incluyen la antigua Copa de la UEFA ni la Recopa de Europa. Las rondas de clasificación no se valoran."},
  conf: {eyebrow: "Liga Conferencia de la UEFA (2021/22 →)", short: "Liga Conferencia", note: "Las rondas de clasificación no se valoran."},
  uefa: {eyebrow: "Competiciones UEFA de clubes", short: "Competiciones UEFA de clubes",
         note: "Una puntuación por club en la Liga de Campeones (1992/93 →), la Liga Europa (2009/10 →) y la Liga Conferencia (2021/22 →). Cada partido se valora con el factor K de su propia competición y fase (ver factores K); dentro de una temporada los partidos se ordenan por fase y después por competición. Como los rivales arrastran sus resultados de las tres competiciones, la puntuación de un club aquí puede diferir en unos pocos puntos de la de la clasificación de una sola competición, incluso si solo jugó en esa (por ejemplo el Real Madrid en la Liga de Campeones)."},
  wc: {eyebrow: "Copa del Mundo de la FIFA", short: "Mundial", groupLabel: t => REGION_ES[t.label] || t.label},
  pl: {eyebrow: "Premier League (Primera División 1888–1992)", sub: "Inglaterra", groupLabel: () => "Inglaterra"},
  ekstraklasa: {eyebrow: "Ekstraklasa (I liga 1927–2008)", sub: "Polonia", groupLabel: () => "Polonia"},
  bundesliga: {eyebrow: "Bundesliga (1963 →)", sub: "Alemania", groupLabel: () => "Alemania",
               note: "La Bundesliga empezó en 1963/64. Tras la reunificación alemana, los clubes de la antigua Alemania del Este empiezan simplemente en 1600 cuando aparecen por primera vez; ese periodo no recibe un tratamiento aparte."},
  spain: {eyebrow: "La Liga (1928/29 →)", sub: "España", groupLabel: () => "España",
          note: "No se jugó liga en 1936–39 (Guerra Civil española). La fase de grupos de promoción/descenso de 1986/87 no se valora. Un partido de 1979/80 (Málaga–Salamanca) falta en todas las fuentes."},
  france: {eyebrow: "Ligue 1 (Division 1 1932/33 →)", sub: "Francia", groupLabel: () => "Francia",
           note: "No se jugó liga en 1939–45 (Segunda Guerra Mundial). La temporada 2019/20 se detuvo en marzo con 279 de 380 partidos disputados."},
  italy: {eyebrow: "Serie A (1929/30 →)", sub: "Italia", groupLabel: () => "Italia",
          note: "Empieza con la primera temporada de tabla única, 1929/30. No se jugó liga en 1943–45 (guerra) y la de 1945/46 (disputada en dos grupos regionales) no se incluye. Faltan 40 de los 420 partidos de 1947/48 en todas las fuentes."},
  euro: {eyebrow: "Eurocopa de la UEFA", short: "Eurocopa", sub: "Europa", groupLabel: () => "Europa"},
  copa: {eyebrow: "Copa América (1993 →)", short: "Copa América", groupLabel: t => REGION_ES[t.label] || t.label,
         note: "Solo se incluyen las ediciones desde 1993: desde entonces el torneo tiene un formato estable (grupos, cuartos de final, semifinales, tercer puesto, final). Las ediciones anteriores eran ligas con formatos cambiantes y registros incompletos."},
  nl: {eyebrow: "Liga de Naciones de la UEFA", short: "Liga de Naciones", groupLabel: t => `División ${t.division}`},
};
if (LANG === "es") {
  const NOUN = {Clubs: ["Clubes", "Club"], Nations: ["Selecciones", "Selección"]}, PER = {Seasons: ["Temporadas", "Temporada"], Editions: ["Ediciones", "Edición"]};
  for (const [k, c] of Object.entries(COMPS)) {
    [c.noun, c.noun1] = NOUN[c.noun]; [c.period, c.period1] = PER[c.period];
    if (c.live) c.live = "actualizado a diario";
    if (!COMPS_ES[k] || !COMPS_ES[k].groupLabel) { const g = c.groupLabel; c.groupLabel = (t, i) => { const v = g(t, i); return COUNTRY_ES[v] || v; }; }
    Object.assign(c, COMPS_ES[k] || {});
  }
}
// Display name of a team: national teams get their Spanish name; routes and search always use the English one.
const tn = t => (LANG === "es" && C && C.flags ? COUNTRY_ES[t.name] || t.name : t.name);
const TABS = ["ranking", "history", "stats", "compare", "about"];
const TAB_ES = {ranking: "Ranking", history: "Historial", stats: "Estadísticas", compare: "Comparar", about: "Información"};
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const cache = {};
const fmtTime = iso => new Date(iso).toLocaleString(L("en-GB", "es-ES"), {day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit"});
let D, C, T, route = {comp: "", tab: "ranking", team: ""};

async function load(key) {
  if (!cache[key]) {
    // data files are cached by the browser/CDN: version them with the build time so a fresh
    // deploy is never paired with stale data
    if (!window.buildId) {
      try { window.meta = await (await fetch(ROOT + "data/meta.json", {cache: "no-store"})).json(); window.buildId = window.meta.built; } catch (e) { window.buildId = Date.now(); }
    }
    const r = await fetch(`${ROOT}${COMPS[key].file}?v=${encodeURIComponent(window.buildId)}`);
    if (!r.ok) throw new Error(r.status);
    cache[key] = prepare(await r.json());
  }
  return cache[key];
}

// Per-team timelines + per-period stats derived from the match list.
function prepare(d) {
  d.tl = d.teams.map(() => []);
  const start = d.teams.map(() => 1600);
  d.periods = [];
  d.matches.forEach((m, i) => {
    const [per, ph, a, ga, b, gb, dec, pa, pb, ea, eb] = m;
    if (d.periods[d.periods.length - 1] !== per) d.periods.push(per);
    d.tl[a].push({i, per, ph, opp: b, gf: ga, ga: gb, dec, pf: pa, pa: pb, before: start[a], after: ea});
    d.tl[b].push({i, per, ph, opp: a, gf: gb, ga: ga, dec, pf: pb, pa: pa, before: start[b], after: eb});
    start[a] = ea; start[b] = eb;
  });
  const last = d.periods[d.periods.length - 1];
  d.delta = d.tl.map(tl => { const x = tl.filter(e => e.per === last); return x.length ? x[x.length - 1].after - x[0].before : 0; });
  d.last = last;
  return d;
}

const flagUrl = t => t.iso ? `https://flagcdn.com/w40/${t.iso}.png` : "";
// Initials shown in the frame when a club has no crest (or the image fails to load).
const monogram = name => {
  const w = name.replace(/[().,\/]/g, " ").split(/\s+/).filter(x => x && !/^(FC|AFC|SC|KS|GKS|SK|CF|of|de|the|1\.)$/i.test(x));
  const s = w.length > 1 ? w.slice(0, 3).map(x => x[0]).join("") : (w[0] || name).slice(0, 3);
  return s.toUpperCase();
};
const icon = (t, size = "") => {
  const u = C && C.flags ? flagUrl(t) : t.logo || "", m = monogram(t.name);
  return `<span class="ico${size ? " " + size : ""}">${u ? `<img src="${esc(u)}" alt="" loading="lazy" data-mg="${esc(m)}" onerror="this.parentNode.innerHTML='<b class=mg>'+this.dataset.mg+'</b>'">` : `<b class="mg">${esc(m)}</b>`}</span>`;
};
const eloColor = () => "var(--ink)";
const tagHtml = ph => { const p = D.phases[ph]; return `<span class="tag"${p.label === "PO" ? ' title="${L("Promotion/relegation play-off between two divisions", "Eliminatoria de ascenso/descenso entre dos divisiones")}"' : ""} style="background:${p.color}30;border-color:${p.color};color:var(--ink)">${p.label}</span>`; };

// ── routing ───────────────────────────────────────────────────────
function parseHash() {
  const [comp = "", tab = "ranking", team = ""] = location.hash.slice(1).split("/").map(decodeURIComponent);
  return {comp: COMPS[comp] ? comp : "", tab: TABS.includes(tab) ? tab : "ranking", team};
}
// Static texts and the language switch (it keeps the current route: the same ranking and tab in the other language)
function chrome() {
  const back = document.querySelector(".back-link"); if (back) back.textContent = L("← All rankings", "← Todos los rankings");
  const base = {en: LANG === "en" ? "./" : "../", es: LANG === "en" ? "es/" : "./"};
  document.querySelectorAll("#lang a").forEach(a => { a.href = base[a.dataset.l] + location.hash; a.classList.toggle("on", a.dataset.l === LANG); });
}
async function render() {
  route = parseHash();
  chrome();
  $("home").hidden = !!route.comp; $("comp").hidden = !route.comp;
  if (!route.comp) return renderHome();
  try { D = await load(route.comp); } catch (e) { $("view").innerHTML = `<div class="empty">${L("FAILED TO LOAD DATA", "ERROR AL CARGAR LOS DATOS")}</div>`; return; }
  C = COMPS[route.comp];
  $("comp-bg").style.backgroundImage = `url('${ROOT}${C.img}')`;
  $("eyebrow").textContent = C.eyebrow;
  $("subtitle").textContent = `${D.periods[0]} – ${D.last}` + (window.meta && window.meta.synced ? ` · ${L("data checked", "datos comprobados")} ${fmtTime(window.meta.synced)}` : "");
  $("stats").innerHTML = [[D.periods.length, C.period], [D.matches.length.toLocaleString(LANG), L("Matches", "Partidos")], [D.teams.length, C.noun]]
    .map(([v, l]) => `<div><div class="stat-val">${v}</div><div class="stat-label">${l}</div></div>`).join("");
  $("tabs").innerHTML = TABS.map(t => `<a class="tab${t === route.tab ? " on" : ""}" href="#${route.comp}/${t}">${L(t, TAB_ES[t])}</a>`).join("");
  document.title = L(`${C.eyebrow} ELO Ranking`, `Ranking ELO – ${C.eyebrow}`);
  ({ranking, history, stats, compare, about})[route.tab]();
}
// Matches that each build found new (data/recent.json: batches of the last 30 days, newest first)
async function recentHtml() {
  let batches = [];
  try { batches = (await (await fetch(`${ROOT}data/recent.json?v=${encodeURIComponent(window.buildId)}`)).json()).batches || []; } catch (e) { return ""; }
  const n = batches.reduce((a, b) => a + b.matches.length, 0);
  const body = batches.slice(0, 12).map(b => {
    const by = new Map();
    b.matches.forEach(m => { if (COMPS[m.c]) by.set(m.c, [...(by.get(m.c) || []), m]); });
    return `<h4>${fmtTime(b.at)} · ${b.matches.length} ${L(b.matches.length === 1 ? "match" : "matches", b.matches.length === 1 ? "partido" : "partidos")}</h4>` + [...by].map(([c, ms]) =>
      `<div class="rc"><a href="#${c}/history">${esc(COMPS[c].short || COMPS[c].eyebrow)}</a></div>` + ms.map(m =>
        `<div class="rm"><span>${esc(m.a)}</span><b>${esc(m.s)}</b><span>${esc(m.b)}</span><i>${esc(m.d || m.p)}</i></div>`).join("")).join("");
  }).join("");
  return `<details class="recent"><summary>${L("Recently added matches", "Partidos añadidos recientemente")}${n ? ` (${n})` : ""}</summary>${body || `<p class="sub">${L("No new matches were found in the last updates.", "No se encontraron partidos nuevos en las últimas actualizaciones.")}</p>`}</details>`;
}
async function renderHome() {
  document.title = L("Football ELO Rankings", "Ranking ELO de fútbol");
  // card artwork without trademarked competition logos: the flag of the country, the flags of the best nations,
  // or the crests of the best clubs of that very ranking
  const art = (d, c) => {
    if (c.flag) return `<img class="bigflag" src="https://flagcdn.com/w320/${c.flag}.png" alt="">`;
    const tiles = d.teams.map(t => c.flags ? (t.iso ? `https://flagcdn.com/w80/${t.iso}.png` : "") : t.logo || "").filter(Boolean).slice(0, 6);
    return `<div class="mosaic">${tiles.map(u => `<img src="${esc(u)}" alt="" loading="lazy" onerror="this.remove()">`).join("")}</div>`;
  };
  const card = async k => {
    const d = await load(k), c = COMPS[k];
    return `<a class="home-card" href="#${k}" style="--c1:${c.c1};--c2:${c.c2}">${art(d, c)}<div class="eyebrow">${c.short || c.eyebrow}</div>
      <h2>${L("ELO Ranking", "Ranking ELO")}</h2><div class="subtitle">${d.periods.length} ${c.period.toLowerCase()} · ${d.matches.length.toLocaleString(LANG)} ${L("matches", "partidos")} · ${d.teams.length} ${c.noun.toLowerCase()}</div>
      <div class="subtitle">${L("through", "hasta")} ${esc(d.last)}${c.live ? " · " + esc(c.live) : ""}</div></a>`;
  };
  const section = async (title, keys) => `<h3 class="section">${title}</h3><div class="cards">${(await Promise.all(keys.map(card))).join("")}</div>`;
  const keys = Object.keys(COMPS);
  $("home-cards").innerHTML = await section(L("International Competitions", "Competiciones internacionales"), keys.filter(k => COMPS[k].flags)) + await section(L("UEFA Competitions", "Competiciones UEFA"), keys.filter(k => !COMPS[k].flags && !COMPS[k].domestic)) + await section(L("National Competitions", "Competiciones nacionales"), keys.filter(k => COMPS[k].domestic));
  const m = window.meta || {};
  const names = Object.values(COMPS).filter(c => c.live).map(c => esc(c.short || c.eyebrow)).join(", "), wcl = esc(cache.wc ? cache.wc.last : ""), eul = esc(cache.euro ? cache.euro.last : ""), cal = esc(cache.copa ? cache.copa.last : "");
  $("home-status").innerHTML = L(`<b>Updates:</b> ${names} refresh automatically every day;
    the World Cup (last edition ${wcl}), European Championship (${eul}) and Copa América (${cal}) update when a new tournament is played.<br>
    Last data check: <b>${m.synced ? fmtTime(m.synced) : "n/a"}</b> · site built: <b>${m.built ? fmtTime(m.built) : "n/a"}</b>`,
  `<b>Actualizaciones:</b> ${names} se actualizan automáticamente cada día;
    el Mundial (última edición ${wcl}), la Eurocopa (${eul}) y la Copa América (${cal}) se actualizan cuando se juega un torneo nuevo.<br>
    Última comprobación de datos: <b>${m.synced ? fmtTime(m.synced) : "n/d"}</b> · sitio generado: <b>${m.built ? fmtTime(m.built) : "n/d"}</b>`);
  $("home-recent").innerHTML = await recentHtml();
}
window.addEventListener("hashchange", render);
window.addEventListener("scroll", () => document.querySelectorAll(".hero-bg").forEach(el => { el.style.transform = `translateY(${Math.round(scrollY * .35)}px)`; }));

// ── ranking ───────────────────────────────────────────────────────
function ranking() {
  const eras = D.eras || null;                 // e.g. Premier League: separate leaderboards per era
  const groups = new Map();
  if (!eras) D.teams.forEach((t, i) => groups.set(C.group(t, i), C.groupLabel(t, i)));
  const state = {g: D.default_era || "", q: ""};
  $("view").innerHTML = `<div class="controls"><input id="q" class="input" placeholder="${L("Search…", "Buscar…")}" autocomplete="off"></div>
    <div class="chips" id="chips"></div><div class="row head"><span>${L("Pos", "Pos.")}</span><span></span><span>${C.noun1 || C.noun.slice(0, -1)}</span><span class="r">ELO</span><span class="r" id="dhead"></span><span class="r mcount">${L("Games", "Partidos")}</span></div><div id="rows"></div>`;
  const draw = () => {
    const era = eras && eras.find(x => x.id === state.g);
    const v = era || {elo: D.teams.map(t => t.elo), matches: D.teams.map(t => t.matches), delta: D.delta, last: D.last};
    const chipList = eras ? [["", L("All", "Todos")], ...eras.map(e => [e.id, e.label])] : [["", L("All", "Todos")], ...[...groups].filter(([k]) => k).sort().map(([k]) => [k, k])];
    const cw = Math.max(...chipList.map(([, l]) => l.length)) * 8 + 24;
    $("chips").innerHTML = chipList
      .map(([k, l]) => `<button class="chip${k === state.g ? " on" : ""}" style="width:${cw}px" data-g="${esc(k)}" title="${esc(groups.get(k) || "")}">${esc(l)}</button>`).join("");
    $("dhead").textContent = `Δ ${v.last}`;
    $("dhead").title = L(`Rating change during ${v.last}`, `Variación de la puntuación durante ${v.last}`);
    let list = D.teams.map((t, i) => i);
    if (era) list = list.filter(i => v.matches[i] > 0).sort((a, b) => v.elo[b] - v.elo[a] || a - b);
    const rank = new Map(list.map((i, r) => [i, r + 1]));            // position within the current leaderboard
    if (!eras && state.g) list = list.filter(i => C.group(D.teams[i], i) === state.g);
    const q = state.q.toLowerCase();
    if (q) list = list.filter(i => [D.teams[i].name, tn(D.teams[i]), ...(D.teams[i].aliases || [])].some(n => n.toLowerCase().includes(q)));
    $("rows").innerHTML = list.map(i => { const t = D.teams[i], dl = v.delta[i], e = v.elo[i], r = rank.get(i);
      return `<div class="row" data-t="${i}"><span class="pos${r <= 3 ? " top" : ""}">${r}</span>${icon(t)}
        <div><div class="name">${esc(tn(t))}</div><div class="sub">${esc(C.sub || C.groupLabel(t, i))}${t.note ? " · " + esc(t.note) : ""}</div></div>
        <span class="elo" style="color:${eloColor(e)}">${e}</span>
        <span class="delta ${dl > 0 ? "up" : dl < 0 ? "down" : "flat"}">${dl > 0 ? "+" + dl : dl || "–"}</span><span class="mcount">${v.matches[i]}</span></div>`; }).join("");
  };
  $("chips").onclick = e => { if (e.target.dataset.g !== undefined) { state.g = e.target.dataset.g; draw(); } };
  $("rows").onclick = e => { const r = e.target.closest(".row"); if (r) location.hash = `#${route.comp}/stats/${encodeURIComponent(D.teams[r.dataset.t].name)}`; };
  $("q").oninput = e => { state.q = e.target.value; draw(); };
  draw();
}

// ── history ───────────────────────────────────────────────────────
const teamOptions = sel => `<option value="">${L("All", "Todos")}</option>` + D.teams.map((t, i) => `<option value="${i}"${sel === i ? " selected" : ""}>${esc(tn(t))}</option>`).join("");
function history() {
  $("view").innerHTML = `<div class="controls"><select id="ht" class="input">${teamOptions()}</select>
    <select id="hp" class="input"><option value="">${L("All periods", "Todos los periodos")}</option>${[...D.periods].reverse().map(p => `<option>${esc(p)}</option>`).join("")}</select></div><div id="list"></div>`;
  const draw = () => {
    const t = $("ht").value, p = $("hp").value;
    const rows = []; for (let i = D.matches.length - 1; i >= 0 && rows.length < 400; i--) {
      const m = D.matches[i];
      if ((!p || m[0] === p) && (!t || m[2] == t || m[4] == t)) rows.push(m);
    }
    $("list").innerHTML = rows.length ? rows.map(matchRow).join("") : `<div class="empty">${L("NO MATCHES", "SIN PARTIDOS")}</div>`;
  };
  $("ht").onchange = $("hp").onchange = draw; draw();
}
function score(m) {
  const [, , , ga, , gb, dec, pa, pb] = m;
  return `${ga}–${gb}` + (dec === "pw" ? ` <span class="pill">${L("(pens)", "(pen.)")}</span>` : dec === "pen" ? ` <span class="pill">(${pa}–${pb} p)</span>` : dec === "aet" ? ` <span class="pill">${L("aet", "prór.")}</span>` : "");
}
function matchRow(m) {
  const [per, ph, a, ga, b, gb, dec, pa, pb, ea, eb] = m;
  const wa = ga > gb || (ga === gb && pa > pb), wb = gb > ga || (ga === gb && pb > pa);
  // crests sit at the outer ends of the two name columns, so the layout is symmetric whatever the name length
  return `<div class="match"><span class="pill ph">${tagHtml(ph)}</span>${icon(D.teams[a], "sm")}<span class="a${wa ? " win" : ""}">${esc(tn(D.teams[a]))}</span>
    <span class="sc">${score(m)}</span><span class="b${wb ? " win" : ""}">${esc(tn(D.teams[b]))}</span>${icon(D.teams[b], "sm")}<span class="d">${esc(per)} · ${ea}/${eb}</span></div>`;
}

// ── stats / compare ───────────────────────────────────────────────
let chart;
function drawChart(canvas, series) {
  if (chart) chart.destroy();
  if (typeof Chart === "undefined") { canvas.replaceWith(Object.assign(document.createElement("p"), {className: "sub", textContent: L("Chart library failed to load.", "No se pudo cargar la librería de gráficos.")})); return; }
  Chart.defaults.font.family = "Barlow, system-ui, sans-serif";
  chart = new Chart(canvas, {type: "line", data: {labels: D.periods, datasets: series.map(s => ({label: s.label, data: D.periods.map(p => s.map[p] ?? null),
    borderColor: s.color, backgroundColor: s.color, spanGaps: true, tension: .25, pointRadius: 2, borderWidth: 2}))},
    options: {interaction: {mode: "index", intersect: false}, scales: {x: {ticks: {color: "#6b675e", maxTicksLimit: 12}, grid: {color: "#e3ded0"}}, y: {ticks: {color: "#6b675e"}, grid: {color: "#e3ded0"}}},
      plugins: {legend: {labels: {color: "#4d4a43"}}}}});
}
const periodElo = i => { const m = {}; D.tl[i].forEach(e => m[e.per] = e.after); return m; };
const periodStats = i => { const s = new Map(); D.tl[i].forEach(e => { const x = s.get(e.per) || {start: e.before, n: 0}; x.end = e.after; x.n++; s.set(e.per, x); }); return s; };
// Highest rating after any single match (what the History tab shows as "ea/eb"), not the end-of-period value.
// A team that never rose above its starting rating peaks at 1600, before its first match.
function allTimeHigh(i) {
  let best = null;
  D.tl[i].forEach(e => { if (!best || e.after > best.after) best = e; });
  if (!best || best.after <= 1600) return {elo: 1600, start: true};
  return {elo: best.after, per: best.per, e: best};
}
function athHtml(i) {
  const h = allTimeHigh(i);
  if (h.start) return `<div class="ath">${L("ALL-TIME HIGH", "MÁXIMO HISTÓRICO")} <b>${h.elo}</b> · ${L("starting rating", "puntuación inicial")}</div>`;
  const m = D.matches[h.e.i];
  return `<div class="ath">${L("ALL-TIME HIGH", "MÁXIMO HISTÓRICO")} <b>${h.elo}</b> · ${esc(h.per)} · ${L("after", "tras")} ${esc(tn(D.teams[m[2]]))} ${score(m)} ${esc(tn(D.teams[m[4]]))}</div>`;
}
function seasonTable(i) {
  return `<table class="seasons"><tr><th>${C.period1 || C.period.slice(0, -1)}</th><th>${L("Start", "Inicio")}</th><th>${L("End", "Fin")}</th><th>Δ</th><th>${L("Games", "Partidos")}</th></tr>${[...periodStats(i)].reverse().map(([p, x]) => {
    const d = x.end - x.start; return `<tr><td>${esc(p)}</td><td>${x.start}</td><td>${x.end}</td><td class="${d > 0 ? "up" : d < 0 ? "down" : "flat"}">${d > 0 ? "+" : ""}${d}</td><td>${x.n}</td></tr>`; }).join("")}</table>`;
}
function stats() {
  const cur = D.teams.findIndex(t => t.name === route.team);
  $("view").innerHTML = `<div class="controls"><select id="st" class="input"><option value="">${L("Select…", "Seleccionar…")}</option>${D.teams.map((t, i) => `<option value="${i}"${i === cur ? " selected" : ""}>${esc(tn(t))}</option>`).join("")}</select></div><div id="out"></div>`;
  $("st").onchange = () => { location.hash = `#${route.comp}/stats/${$("st").value === "" ? "" : encodeURIComponent(D.teams[$("st").value].name)}`; };
  if (cur < 0) { $("out").innerHTML = `<div class="empty">${L("SELECT A TEAM TO VIEW ELO PROGRESSION", "SELECCIONA UN EQUIPO PARA VER SU EVOLUCIÓN ELO")}</div>`; return; }
  const t = D.teams[cur];
  $("out").innerHTML = `<div class="card"><h3 style="display:flex;align-items:center;gap:10px">${icon(t)}${esc(tn(t))} · ${t.elo} ELO · #${cur + 1}</h3>${athHtml(cur)}<canvas id="ch" height="110"></canvas>${t.note ? `<p class="sub" style="margin-top:8px">${esc(t.note)}</p>` : ""}</div>
    <div class="card">${seasonTable(cur)}</div><div class="card">${D.tl[cur].slice().reverse().slice(0, 60).map(e => matchRow(D.matches[e.i])).join("")}</div>`;
  drawChart($("ch"), [{label: tn(t), map: periodElo(cur), color: "#b3261e"}]);
}
function compare() {
  const a = D.teams.findIndex(t => t.name === route.team.split("~")[0]), b = D.teams.findIndex(t => t.name === route.team.split("~")[1]);
  $("view").innerHTML = `<div class="controls"><select id="ca" class="input">${teamOptions(a)}</select><span class="mono">vs</span><select id="cb" class="input">${teamOptions(b)}</select></div><div id="out"></div>`;
  const go = () => { const x = $("ca").value, y = $("cb").value; location.hash = `#${route.comp}/compare/${x === "" ? "" : encodeURIComponent(D.teams[x].name)}${y === "" ? "" : "~" + encodeURIComponent(D.teams[y].name)}`; };
  $("ca").onchange = $("cb").onchange = go;
  if (a < 0 || b < 0) { $("out").innerHTML = `<div class="empty">${L("SELECT TWO TEAMS TO COMPARE", "SELECCIONA DOS EQUIPOS PARA COMPARAR")}</div>`; return; }
  const h2h = D.tl[a].filter(e => e.opp === b);
  const w = h2h.filter(e => e.gf > e.ga || (e.gf === e.ga && e.pf > e.pa)).length, l = h2h.filter(e => e.gf < e.ga || (e.gf === e.ga && e.pf < e.pa)).length;
  $("out").innerHTML = `<div class="card"><canvas id="ch" height="110"></canvas></div>
    <div class="card"><h3>${L("Head to head", "Cara a cara")}</h3><p>${esc(tn(D.teams[a]))} ${w}${L("W", "G")} · ${h2h.length - w - l}${L("D", "E")} · ${l}${L("L", "P")} vs ${esc(tn(D.teams[b]))} (${h2h.length} ${L("matches", "partidos")})</p></div>
    ${h2h.length ? `<div class="card">${h2h.slice().reverse().map(e => matchRow(D.matches[e.i])).join("")}</div>` : ""}`;
  drawChart($("ch"), [{label: tn(D.teams[a]), map: periodElo(a), color: "#b3261e"}, {label: tn(D.teams[b]), map: periodElo(b), color: "#1f4e79"}]);
}

// ── about ─────────────────────────────────────────────────────────
function about() {
  const ph = Object.entries(D.phases).map(([k, p]) => `<li>${tagHtml(k)} K = ${p.k}</li>`).join("");
  const leagues = ["pl", "ekstraklasa", "bundesliga", "spain", "france", "italy"].includes(route.comp);
  const legs = route.comp === "ucl" ? `<li>${L("Two-legged ties: each leg is rated separately.", "Eliminatorias a doble partido: cada partido se valora por separado.")}</li>` : "";
  const nl = route.comp === "nl" ? L(`<li>K depends on the division the match is played in (A 24 · B 12 · C 8 · D 4), so a win in a lower division moves the rating less. There is one common ranking for all divisions.</li><li>Quarter-finals: K of Division A. Semi-finals, 3rd place and final: K 32. Promotion/relegation play-offs between two divisions use the K of the lower one. <b>PO</b> in the history marks these promotion/relegation play-offs.</li><li>The Nations League is played every two years (2018/19, 2020/21, 2022/23 …); the years in between have no edition.</li><li>Two-legged ties: each leg is rated separately.</li>`,
    `<li>K depende de la división en la que se juega el partido (A 24 · B 12 · C 8 · D 4), por lo que una victoria en una división inferior mueve menos la puntuación. Hay un único ranking común para todas las divisiones.</li><li>Cuartos de final: K de la División A. Semifinales, tercer puesto y final: K 32. Las eliminatorias de ascenso/descenso entre dos divisiones usan la K de la inferior. <b>PO</b> en el historial marca estas eliminatorias de ascenso/descenso.</li><li>La Liga de Naciones se juega cada dos años (2018/19, 2020/21, 2022/23 …); los años intermedios no hay edición.</li><li>Eliminatorias a doble partido: cada partido se valora por separado.</li>`) : "";
  const lg = leagues ? L(`<li>League matches only: no extra time or penalties.</li><li>Clubs keep their rating while outside the top flight.</li><li>The era buttons only filter the years: each club has one continuous rating, shown as it stood at the end of that era (games and Δ count that era only).</li>`,
    `<li>Solo partidos de liga: sin prórroga ni penaltis.</li><li>Los clubes conservan su puntuación mientras están fuera de la máxima categoría.</li><li>Los botones de época solo filtran los años: cada club tiene una puntuación continua, mostrada tal como estaba al final de esa época (los partidos y la Δ cuentan solo esa época).</li>`) : "";
  const src = C.source || lnk("https://github.com/openfootball", "openfootball") + L(", football-data.org and Wikipedia", ", football-data.org y Wikipedia");
  $("view").innerHTML = `<div class="grid2">
    <div class="card"><h3>${L("ELO formula", "Fórmula ELO")}</h3><div class="formula">R ← R + K × (S − E)</div><p>E = 1 / (1 + 10^((R_${L("opp", "rival")} − R_${L("self", "propia")}) / 400))</p>
      <p>${L("S: 1 win · 0.5 draw · 0 loss. Everyone starts at 1600.", "S: 1 victoria · 0,5 empate · 0 derrota. Todos empiezan en 1600.")}</p></div>
    <div class="card"><h3>${L("K-factors", "Factores K")}</h3><ul style="list-style:none;padding:0">${ph}</ul></div>
    <div class="card"><h3>${L("Extra time &amp; penalties", "Prórroga y penaltis")}</h3><ul><li>${L("Score after extra time is used.", "Se usa el resultado tras la prórroga.")}</li><li>${L("If a match is decided on penalties, the shoot-out winner counts as the winner.", "Si un partido se decide en penaltis, el ganador de la tanda cuenta como ganador.")}</li>
      ${legs}${nl}${lg}</ul></div>
    <div class="card"><h3>${L("Data", "Datos")}</h3><ul><li>${D.periods[0]} – ${D.last}, ${D.matches.length.toLocaleString(LANG)} ${L("matches", "partidos")}</li>
      ${C.note ? `<li>${C.note}</li>` : ""}<li>${L("Updated daily from", "Actualizado a diario desde")} ${src}</li>
      <li>${L("Renamed / merged teams are listed in", "Los equipos renombrados o fusionados figuran en el")} ${lnk(`${REPO}/blob/main/data/teams_${route.comp}.json`, L("teams file", "archivo de equipos"))}</li></ul></div></div>`;
}
render();
