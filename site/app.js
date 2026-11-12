"use strict";
// Four languages share this file and the data: the English page (index.html) and es/, pt/, pl/ (index.html with
// window.LANG = "es" | "pt" | "pl" and window.ROOT = "../"). Texts live in i18n.js; L(key, ...args) picks the text.
const LANG = I18N.langs.includes(window.LANG) ? window.LANG : "en";
const LIDX = I18N.langs.indexOf(LANG);
const ROOT = window.ROOT || "";
const L = (key, ...args) => { const e = I18N.dict[key] || [key]; return (e[LIDX] || e[0]).replace(/\{(\d+)\}/g, (_, i) => (args[i] === undefined ? "" : args[i])); };
// "1 match", "2-4 mecze", "5 meczów": the plural word after a number
const matchWord = n => L(n === 1 ? "match_1" : LANG === "pl" && n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? "match_few" : "matches_n");
const REPO = "https://github.com/enterdesign/footballelo";
const lnk = (href, text) => `<a href="${href}" style="color:var(--accent);text-decoration:underline">${text}</a>`;
const INTL = lnk("https://github.com/martj42/international_results", "international_results");
const WIKI_LINK = lnk("https://en.wikipedia.org", L("wiki_en"));
const WIKI = `${WIKI_LINK} (CC BY-SA)`;
const WIKI_OPENFOOTBALL = `${lnk("https://github.com/openfootball", "openfootball")}, football-data.org ${L("and")} ${WIKI_LINK}`;
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
// Language overrides of the competition cards (names, notes, country line, nouns), see i18n.js
if (LANG !== "en") {
  const nouns = I18N.nouns[LANG], over = I18N.comps[LANG], country = I18N.country[LANG], region = I18N.region[LANG];
  for (const [k, c] of Object.entries(COMPS)) {
    const o = over[k] || {};
    [c.noun, c.noun1, c.nounN] = nouns[c.noun]; [c.period, c.period1, c.periodN] = nouns[c.period];
    if (c.live) c.live = I18N.live[LANG];
    const g = c.groupLabel;
    c.groupLabel = o.sub ? () => o.sub : k === "nl" ? t => `${I18N.division[LANG]} ${t.division}` : (t, i) => { const v = g(t, i); return country[v] || region[v] || v; };
    Object.assign(c, o);
  }
}
// Display name of a team: national teams get their name in the language of the page; routes and search keep the English one.
const tn = t => (LANG !== "en" && C && C.flags ? I18N.country[LANG][t.name] || t.name : t.name);
const TABS = ["ranking", "history", "stats", "compare", "about"];
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const cache = {};
const fmtTime = iso => new Date(iso).toLocaleString(I18N.locale[LANG], {day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit"});
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
const tagHtml = ph => { const p = D.phases[ph]; return `<span class="tag"${p.label === "PO" ? ' title="${L("po_tip")}"' : ""} style="background:${p.color}30;border-color:${p.color};color:var(--ink)">${p.label}</span>`; };

// ── routing ───────────────────────────────────────────────────────
function parseHash() {
  const [comp = "", tab = "ranking", team = ""] = location.hash.slice(1).split("/").map(decodeURIComponent);
  return {comp: COMPS[comp] ? comp : "", tab: TABS.includes(tab) ? tab : "ranking", team};
}
// Static texts and the language switch (it keeps the current route: the same ranking and tab in the other language)
function chrome() {
  const back = document.querySelector(".back-link"); if (back) back.textContent = L("all_rankings");
  const up = LANG === "en" ? "" : "../";
  document.querySelectorAll("#lang a").forEach(a => {
    const l = a.dataset.l;
    a.href = (l === LANG ? "./" : up + (l === "en" ? "" : l + "/")) + location.hash;
    a.classList.toggle("on", l === LANG);
  });
}
async function render() {
  route = parseHash();
  chrome();
  $("home").hidden = !!route.comp; $("comp").hidden = !route.comp;
  if (!route.comp) return renderHome();
  try { D = await load(route.comp); } catch (e) { $("view").innerHTML = `<div class="empty">${L("load_failed")}</div>`; return; }
  C = COMPS[route.comp];
  $("comp-bg").style.backgroundImage = `url('${ROOT}${C.img}')`;
  $("eyebrow").textContent = C.eyebrow;
  $("subtitle").textContent = `${D.periods[0]} – ${D.last}` + (window.meta && window.meta.synced ? ` · ${L("data_checked")} ${fmtTime(window.meta.synced)}` : "");
  $("stats").innerHTML = [[D.periods.length, C.period], [D.matches.length.toLocaleString(LANG), L("matches_label")], [D.teams.length, C.noun]]
    .map(([v, l]) => `<div><div class="stat-val">${v}</div><div class="stat-label">${l}</div></div>`).join("");
  $("tabs").innerHTML = TABS.map(t => `<a class="tab${t === route.tab ? " on" : ""}" href="#${route.comp}/${t}">${L("tab_" + t)}</a>`).join("");
  document.title = L("doc_title", C.eyebrow);
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
    return `<h4>${fmtTime(b.at)} · ${b.matches.length} ${matchWord(b.matches.length)}</h4>` + [...by].map(([c, ms]) =>
      `<div class="rc"><a href="#${c}/history">${esc(COMPS[c].short || COMPS[c].eyebrow)}</a></div>` + ms.map(m =>
        `<div class="rm"><span>${esc(m.a)}</span><b>${esc(m.s)}</b><span>${esc(m.b)}</span><i>${esc(m.d || m.p)}</i></div>`).join("")).join("");
  }).join("");
  return `<details class="recent"><summary>${L("recent")}${n ? ` (${n})` : ""}</summary>${body || `<p class="sub">${L("recent_none")}</p>`}</details>`;
}
// ── home tiles: favourites + order, saved only in this browser (localStorage) ──────────────
const LAYOUT_KEY = "elo.layout.v1";
const GROUPS = ["intl", "uefa", "national"];
const groupOf = k => (COMPS[k].flags ? "intl" : COMPS[k].domestic ? "national" : "uefa");
const SEC_KEY = {intl: "sec_intl", uefa: "sec_uefa", national: "sec_national"};
let layout = {fav: [], order: {}}, editing = false;
try {
  const saved = JSON.parse(localStorage.getItem(LAYOUT_KEY) || "null");
  const strs = v => (Array.isArray(v) ? v.filter(x => typeof x === "string") : []);
  if (saved && typeof saved === "object") layout = {fav: strs(saved.fav), order: Object.fromEntries(GROUPS.map(g => [g, strs((saved.order || {})[g])]))};
} catch (e) { /* storage unavailable or corrupt: the default layout is used */ }
const saveLayout = () => { try { localStorage.setItem(LAYOUT_KEY, JSON.stringify(layout)); } catch (e) { /* kept in memory for this visit */ } };
// every key of a group in the user's order (saved order first, keys not seen before at the end in the default order)
const fullOrder = g => {
  const def = Object.keys(COMPS).filter(k => groupOf(k) === g), saved = (layout.order[g] || []).filter(k => def.includes(k));
  return [...saved, ...def.filter(k => !saved.includes(k))];
};
const favKeys = () => [...new Set(layout.fav)].filter(k => COMPS[k]);
const shown = g => fullOrder(g).filter(k => !favKeys().includes(k));
function moveTile(group, k, to) {                       // to: -1 / +1 (one place) or a key to drop before
  if (group === "fav") {
    const f = favKeys(), i = f.indexOf(k); if (i < 0) return;
    f.splice(i, 1);
    const j = typeof to === "string" ? f.indexOf(to) : Math.min(Math.max(i + to, 0), f.length);
    f.splice(j < 0 ? f.length : j, 0, k); layout.fav = f;
  } else {
    const ord = fullOrder(group), vis = shown(group), i = ord.indexOf(k);
    if (typeof to === "string") { ord.splice(i, 1); const j = ord.indexOf(to); ord.splice(j < 0 ? ord.length : j, 0, k); }
    else { const n = vis[vis.indexOf(k) + to]; if (n === undefined) return; const j = ord.indexOf(n); [ord[i], ord[j]] = [ord[j], ord[i]]; }
    layout.order[group] = ord;
  }
  saveLayout();
}
// card artwork without trademarked competition logos: the flag of the country, the flags of the best nations,
// or the crests of the best clubs of that very ranking
const art = (d, c) => {
  if (c.flag) return `<img class="bigflag" src="https://flagcdn.com/w320/${c.flag}.png" alt="">`;
  const tiles = d.teams.map(t => c.flags ? (t.iso ? `https://flagcdn.com/w80/${t.iso}.png` : "") : t.logo || "").filter(Boolean).slice(0, 6);
  return `<div class="mosaic">${tiles.map(u => `<img src="${esc(u)}" alt="" loading="lazy" onerror="this.remove()">`).join("")}</div>`;
};
const tile = (k, group) => {
  const d = cache[k], c = COMPS[k], fav = favKeys().includes(k);
  return `<div class="tile" data-k="${k}" data-g="${group}"${editing ? ' draggable="true"' : ""}>
    <a class="home-card" href="#${k}" style="--c1:${c.c1};--c2:${c.c2}">${art(d, c)}<div class="eyebrow">${c.short || c.eyebrow}</div>
      <h2>${L("elo_ranking")}</h2><div class="subtitle">${d.periods.length} ${c.periodN || c.period.toLowerCase()} · ${d.matches.length.toLocaleString(LANG)} ${L("matches_n")} · ${d.teams.length} ${c.nounN || c.noun.toLowerCase()}</div>
      <div class="subtitle">${L("through")} ${esc(d.last)}${c.live ? " · " + esc(c.live) : ""}</div></a>
    <button class="star" data-a="star" aria-pressed="${fav}" title="${L(fav ? "fav_remove" : "fav_add")}" aria-label="${L(fav ? "fav_remove" : "fav_add")}">${fav ? "★" : "☆"}</button>
    <span class="mv"><button data-a="mv" data-d="-1" title="${L("move_up")}" aria-label="${L("move_up")}">↑</button><button data-a="mv" data-d="1" title="${L("move_down")}" aria-label="${L("move_down")}">↓</button></span></div>`;
};
function drawCards() {
  const fav = favKeys(), sec = (title, group, keys) => `<h3 class="section">${title}</h3><div class="cards" data-g="${group}">${keys.map(k => tile(k, group)).join("")}</div>`;
  const root = $("home-cards");
  root.className = editing ? "editing" : "";
  root.innerHTML = `<div class="layout-bar">${editing ? `<span class="hint">${L("layout_hint")}</span>` : ""}
      <button data-a="reset"${editing ? "" : " hidden"}>${L("reset_layout")}</button><button data-a="edit" class="${editing ? "on" : ""}">${L(editing ? "done" : "customize")}</button></div>`
    + (fav.length ? sec("★ " + L("fav_section"), "fav", fav) : "") + GROUPS.map(g => sec(L(SEC_KEY[g]), g, shown(g))).join("");
}
function wireHome() {
  const root = $("home-cards");
  root.onclick = e => {
    const btn = e.target.closest("button[data-a]"); if (!btn) return;
    const t = btn.closest(".tile"), a = btn.dataset.a;
    if (a === "edit") editing = !editing;
    else if (a === "reset") { layout = {fav: [], order: {}}; saveLayout(); }
    else if (a === "star") { const k = t.dataset.k; layout.fav = favKeys().includes(k) ? favKeys().filter(x => x !== k) : [...favKeys(), k]; saveLayout(); }
    else if (a === "mv") moveTile(t.dataset.g, t.dataset.k, +btn.dataset.d);
    drawCards();
  };
  let dragged = null;                                   // drag and drop (desktop): a tile moves only inside its own group
  root.ondragstart = e => { const t = e.target.closest && e.target.closest(".tile"); if (!t || !editing) return; dragged = t; t.classList.add("dragging"); e.dataTransfer.effectAllowed = "move"; try { e.dataTransfer.setData("text/plain", t.dataset.k); } catch (x) { /* some browsers need data */ } };
  root.ondragover = e => { const t = e.target.closest && e.target.closest(".tile"); if (dragged && t && t !== dragged && t.dataset.g === dragged.dataset.g) { e.preventDefault(); root.querySelectorAll(".over").forEach(x => x.classList.remove("over")); t.classList.add("over"); } };
  root.ondrop = e => { const t = e.target.closest && e.target.closest(".tile"); if (dragged && t && t !== dragged && t.dataset.g === dragged.dataset.g) { e.preventDefault(); moveTile(dragged.dataset.g, dragged.dataset.k, t.dataset.k); dragged = null; drawCards(); } };
  root.ondragend = () => { dragged = null; root.querySelectorAll(".dragging,.over").forEach(x => x.classList.remove("dragging", "over")); };
}
async function renderHome() {
  document.title = L("home_title");
  await Promise.all(Object.keys(COMPS).map(load));
  drawCards(); wireHome();
  const m = window.meta || {};
  const names = Object.values(COMPS).filter(c => c.live).map(c => esc(c.short || c.eyebrow)).join(", ");
  $("home-status").innerHTML = L("home_status", names, esc(cache.wc ? cache.wc.last : ""), esc(cache.euro ? cache.euro.last : ""), esc(cache.copa ? cache.copa.last : ""),
    m.synced ? fmtTime(m.synced) : L("na"), m.built ? fmtTime(m.built) : L("na"));
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
  $("view").innerHTML = `<div class="controls"><input id="q" class="input" placeholder="${L("search")}" autocomplete="off"></div>
    <div class="chips" id="chips"></div><div class="row head"><span>${L("pos")}</span><span></span><span>${C.noun1 || C.noun.slice(0, -1)}</span><span class="r">ELO</span><span class="r" id="dhead"></span><span class="r mcount">${L("games")}</span></div><div id="rows"></div>`;
  const draw = () => {
    const era = eras && eras.find(x => x.id === state.g);
    const v = era || {elo: D.teams.map(t => t.elo), matches: D.teams.map(t => t.matches), delta: D.delta, last: D.last};
    const chipList = eras ? [["", L("all")], ...eras.map(e => [e.id, e.label])] : [["", L("all")], ...[...groups].filter(([k]) => k).sort().map(([k]) => [k, k])];
    const cw = Math.max(...chipList.map(([, l]) => l.length)) * 8 + 24;
    $("chips").innerHTML = chipList
      .map(([k, l]) => `<button class="chip${k === state.g ? " on" : ""}" style="width:${cw}px" data-g="${esc(k)}" title="${esc(groups.get(k) || "")}">${esc(l)}</button>`).join("");
    $("dhead").textContent = `Δ ${v.last}`;
    $("dhead").title = L("rating_change", v.last);
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
const teamOptions = sel => `<option value="">${L("all")}</option>` + D.teams.map((t, i) => `<option value="${i}"${sel === i ? " selected" : ""}>${esc(tn(t))}</option>`).join("");
function history() {
  $("view").innerHTML = `<div class="controls"><select id="ht" class="input">${teamOptions()}</select>
    <select id="hp" class="input"><option value="">${L("all_periods")}</option>${[...D.periods].reverse().map(p => `<option>${esc(p)}</option>`).join("")}</select></div><div id="list"></div>`;
  const draw = () => {
    const t = $("ht").value, p = $("hp").value;
    const rows = []; for (let i = D.matches.length - 1; i >= 0 && rows.length < 400; i--) {
      const m = D.matches[i];
      if ((!p || m[0] === p) && (!t || m[2] == t || m[4] == t)) rows.push(m);
    }
    $("list").innerHTML = rows.length ? rows.map(matchRow).join("") : `<div class="empty">${L("no_matches")}</div>`;
  };
  $("ht").onchange = $("hp").onchange = draw; draw();
}
function score(m) {
  const [, , , ga, , gb, dec, pa, pb] = m;
  return `${ga}–${gb}` + (dec === "pw" ? ` <span class="pill">${L("pens")}</span>` : dec === "pen" ? ` <span class="pill">(${pa}–${pb} p)</span>` : dec === "aet" ? ` <span class="pill">${L("aet")}</span>` : "");
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
  if (typeof Chart === "undefined") { canvas.replaceWith(Object.assign(document.createElement("p"), {className: "sub", textContent: L("chart_failed")})); return; }
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
  if (h.start) return `<div class="ath">${L("ath")} <b>${h.elo}</b> · ${L("start_rating")}</div>`;
  const m = D.matches[h.e.i];
  return `<div class="ath">${L("ath")} <b>${h.elo}</b> · ${esc(h.per)} · ${L("after")} ${esc(tn(D.teams[m[2]]))} ${score(m)} ${esc(tn(D.teams[m[4]]))}</div>`;
}
function seasonTable(i) {
  return `<table class="seasons"><tr><th>${C.period1 || C.period.slice(0, -1)}</th><th>${L("start")}</th><th>${L("end")}</th><th>Δ</th><th>${L("games")}</th></tr>${[...periodStats(i)].reverse().map(([p, x]) => {
    const d = x.end - x.start; return `<tr><td>${esc(p)}</td><td>${x.start}</td><td>${x.end}</td><td class="${d > 0 ? "up" : d < 0 ? "down" : "flat"}">${d > 0 ? "+" : ""}${d}</td><td>${x.n}</td></tr>`; }).join("")}</table>`;
}
function stats() {
  const cur = D.teams.findIndex(t => t.name === route.team);
  $("view").innerHTML = `<div class="controls"><select id="st" class="input"><option value="">${L("select")}</option>${D.teams.map((t, i) => `<option value="${i}"${i === cur ? " selected" : ""}>${esc(tn(t))}</option>`).join("")}</select></div><div id="out"></div>`;
  $("st").onchange = () => { location.hash = `#${route.comp}/stats/${$("st").value === "" ? "" : encodeURIComponent(D.teams[$("st").value].name)}`; };
  if (cur < 0) { $("out").innerHTML = `<div class="empty">${L("select_team")}</div>`; return; }
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
  if (a < 0 || b < 0) { $("out").innerHTML = `<div class="empty">${L("select_two")}</div>`; return; }
  const h2h = D.tl[a].filter(e => e.opp === b);
  const w = h2h.filter(e => e.gf > e.ga || (e.gf === e.ga && e.pf > e.pa)).length, l = h2h.filter(e => e.gf < e.ga || (e.gf === e.ga && e.pf < e.pa)).length;
  $("out").innerHTML = `<div class="card"><canvas id="ch" height="110"></canvas></div>
    <div class="card"><h3>${L("h2h")}</h3><p>${esc(tn(D.teams[a]))} ${w}${L("w")} · ${h2h.length - w - l}${L("d")} · ${l}${L("l")} vs ${esc(tn(D.teams[b]))} (${h2h.length} ${L("matches_n")})</p></div>
    ${h2h.length ? `<div class="card">${h2h.slice().reverse().map(e => matchRow(D.matches[e.i])).join("")}</div>` : ""}`;
  drawChart($("ch"), [{label: tn(D.teams[a]), map: periodElo(a), color: "#b3261e"}, {label: tn(D.teams[b]), map: periodElo(b), color: "#1f4e79"}]);
}

// ── about ─────────────────────────────────────────────────────────
function about() {
  const ph = Object.entries(D.phases).map(([k, p]) => `<li>${tagHtml(k)} K = ${p.k}</li>`).join("");
  const leagues = ["pl", "ekstraklasa", "bundesliga", "spain", "france", "italy"].includes(route.comp);
  const legs = route.comp === "ucl" ? `<li>${L("two_legs")}</li>` : "";
  const nl = route.comp === "nl" ? L("about_nl") : "";
  const lg = leagues ? L("about_leagues") : "";
  const src = C.source || lnk("https://github.com/openfootball", "openfootball") + L("src_default");
  $("view").innerHTML = `<div class="grid2">
    <div class="card"><h3>${L("formula")}</h3><div class="formula">R ← R + K × (S − E)</div><p>E = 1 / (1 + 10^((R_${L("opp")} − R_${L("self")}) / 400))</p>
      <p>${L("s_line")}</p></div>
    <div class="card"><h3>${L("k_factors")}</h3><ul style="list-style:none;padding:0">${ph}</ul></div>
    <div class="card"><h3>${L("et_h")}</h3><ul><li>${L("et1")}</li><li>${L("et2")}</li>
      ${legs}${nl}${lg}</ul></div>
    <div class="card"><h3>${L("data_h")}</h3><ul><li>${D.periods[0]} – ${D.last}, ${D.matches.length.toLocaleString(LANG)} ${L("matches_n")}</li>
      ${C.note ? `<li>${C.note}</li>` : ""}<li>${L("updated_from")} ${src}</li>
      <li>${L("renamed")} ${lnk(`${REPO}/blob/main/data/teams_${route.comp}.json`, L("teams_file"))}</li></ul></div></div>`;
}
render();
