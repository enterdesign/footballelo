"use strict";
const REPO = "https://github.com/enterdesign/footballelo";
const INTL = `<a href="https://github.com/martj42/international_results" style="color:var(--accent);text-decoration:underline">international_results</a>`;
const WIKI = `<a href="https://en.wikipedia.org" style="color:var(--accent);text-decoration:underline">English Wikipedia</a> (CC BY-SA)`;
const COMPS = {
  ucl: {file: "data/ucl.json", img: "img/ucl.jpg", eyebrow: "UEFA Champions League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "1992/93"},
  el:  {file: "data/el.json", img: "img/home.jpg", eyebrow: "UEFA Europa League (2009/10 →)", short: "Europa League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "2009/10", source: WIKI,
        note: "Since the competition was renamed in 2009/10; the earlier UEFA Cup and Cup Winners' Cup are not included. Qualifying rounds are not rated."},
  conf: {file: "data/conf.json", img: "img/home.jpg", eyebrow: "UEFA Conference League (2021/22 →)", short: "Conference League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: t => t.code, groupLabel: t => t.country, first: "2021/22", source: WIKI, note: "Qualifying rounds are not rated."},
  wc:  {file: "data/wc.json", img: "img/wc.jpg", eyebrow: "FIFA World Cup", noun: "Nations", period: "Editions",
        group: t => t.region, groupLabel: t => t.label, first: "1930", flags: true},
  pl:  {file: "data/pl.json", img: "img/home.jpg", eyebrow: "Premier League (First Division 1888–1992)", short: "Premier League", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "England", sub: "England", first: "1888/89"},
  ekstraklasa: {file: "data/ekstraklasa.json", img: "img/home.jpg", eyebrow: "Ekstraklasa (I liga 1927–2008)", short: "Ekstraklasa", noun: "Clubs", period: "Seasons", live: "updated daily",
        group: () => "", groupLabel: () => "Poland", sub: "Poland", first: "1927"},
  euro: {file: "data/euro.json", img: "img/home.jpg", eyebrow: "UEFA European Championship", short: "European Championship", noun: "Nations", period: "Editions",
        group: () => "", groupLabel: () => "Europe", sub: "Europe", first: "1960", flags: true, source: INTL},
  copa: {file: "data/copa.json", img: "img/home.jpg", eyebrow: "Copa América (1993 →)", short: "Copa América", noun: "Nations", period: "Editions",
        group: t => t.region, groupLabel: t => t.label, first: "1993", flags: true, source: INTL,
        note: "Only editions from 1993 are included: since then the tournament has a stable format (groups, quarter-finals, semi-finals, 3rd place, final). Earlier editions were round-robin leagues with changing formats and incomplete records."},
  nl:  {file: "data/nl.json", img: "img/home.jpg", eyebrow: "UEFA Nations League", noun: "Nations", period: "Editions", live: "updated daily",
        group: t => t.division, groupLabel: t => `Division ${t.division}`, first: "2018/19", flags: true,
        source: INTL},
};
const TABS = ["ranking", "history", "stats", "compare", "about"];
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const cache = {};
const fmtTime = iso => new Date(iso).toLocaleString("en-GB", {day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit"});
let D, C, T, route = {comp: "", tab: "ranking", team: ""};

async function load(key) {
  if (!cache[key]) {
    // data files are cached by the browser/CDN: version them with the build time so a fresh
    // deploy is never paired with stale data
    if (!window.buildId) {
      try { window.meta = await (await fetch("data/meta.json", {cache: "no-store"})).json(); window.buildId = window.meta.built; } catch (e) { window.buildId = Date.now(); }
    }
    const r = await fetch(`${COMPS[key].file}?v=${encodeURIComponent(window.buildId)}`);
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
const tagHtml = ph => { const p = D.phases[ph]; return `<span class="tag"${p.label === "PO" ? ' title="Promotion/relegation play-off between two divisions"' : ""} style="background:${p.color}30;border-color:${p.color};color:var(--ink)">${p.label}</span>`; };

// ── routing ───────────────────────────────────────────────────────
function parseHash() {
  const [comp = "", tab = "ranking", team = ""] = location.hash.slice(1).split("/").map(decodeURIComponent);
  return {comp: COMPS[comp] ? comp : "", tab: TABS.includes(tab) ? tab : "ranking", team};
}
async function render() {
  route = parseHash();
  $("home").hidden = !!route.comp; $("comp").hidden = !route.comp;
  if (!route.comp) return renderHome();
  try { D = await load(route.comp); } catch (e) { $("view").innerHTML = `<div class="empty">FAILED TO LOAD DATA</div>`; return; }
  C = COMPS[route.comp];
  $("comp-bg").style.backgroundImage = `url('${C.img}')`;
  $("eyebrow").textContent = C.eyebrow;
  $("subtitle").textContent = `${D.periods[0]} – ${D.last}` + (window.meta && window.meta.synced ? ` · data checked ${fmtTime(window.meta.synced)}` : "");
  $("stats").innerHTML = [[D.periods.length, C.period], [D.matches.length.toLocaleString("en"), "Matches"], [D.teams.length, C.noun]]
    .map(([v, l]) => `<div><div class="stat-val">${v}</div><div class="stat-label">${l}</div></div>`).join("");
  $("tabs").innerHTML = TABS.map(t => `<a class="tab${t === route.tab ? " on" : ""}" href="#${route.comp}/${t}">${t}</a>`).join("");
  document.title = `${C.eyebrow} ELO Ranking`;
  ({ranking, history, stats, compare, about})[route.tab]();
}
async function renderHome() {
  document.title = "Football ELO Rankings";
  const card = async k => {
    const d = await load(k), c = COMPS[k];
    return `<a class="home-card" href="#${k}" style="background-image:url('${c.img}')"><div class="eyebrow">${c.short || c.eyebrow}</div>
      <h2>ELO Ranking</h2><div class="subtitle">${d.periods.length} ${c.period.toLowerCase()} · ${d.matches.length.toLocaleString("en")} matches · ${d.teams.length} ${c.noun.toLowerCase()}</div>
      <div class="subtitle">through ${esc(d.last)}${c.live ? " · " + esc(c.live) : ""}</div></a>`;
  };
  const section = async (title, keys) => `<h3 class="section">${title}</h3><div class="cards">${(await Promise.all(keys.map(card))).join("")}</div>`;
  const keys = Object.keys(COMPS);
  $("home-cards").innerHTML = await section("National teams", keys.filter(k => COMPS[k].flags)) + await section("Club teams", keys.filter(k => !COMPS[k].flags));
  const m = window.meta || {};
  $("home-status").innerHTML = `<b>Updates:</b> ${Object.values(COMPS).filter(c => c.live).map(c => esc(c.short || c.eyebrow)).join(", ")} refresh automatically every day;
    the World Cup (last edition ${esc(cache.wc ? cache.wc.last : "")}), European Championship (${esc(cache.euro ? cache.euro.last : "")}) and Copa América (${esc(cache.copa ? cache.copa.last : "")}) update when a new tournament is played.<br>
    Last data check: <b>${m.synced ? fmtTime(m.synced) : "n/a"}</b> · site built: <b>${m.built ? fmtTime(m.built) : "n/a"}</b>`;
}
window.addEventListener("hashchange", render);
window.addEventListener("scroll", () => document.querySelectorAll(".hero-bg").forEach(el => { el.style.transform = `translateY(${Math.round(scrollY * .35)}px)`; }));

// ── ranking ───────────────────────────────────────────────────────
function ranking() {
  const eras = D.eras || null;                 // e.g. Premier League: separate leaderboards per era
  const groups = new Map();
  if (!eras) D.teams.forEach((t, i) => groups.set(C.group(t, i), C.groupLabel(t, i)));
  const state = {g: D.default_era || "", q: ""};
  $("view").innerHTML = `<div class="controls"><input id="q" class="input" placeholder="Search…" autocomplete="off"></div>
    <div class="chips" id="chips"></div><div class="row head"><span>Pos</span><span></span><span>${C.noun.slice(0, -1)}</span><span class="r">ELO</span><span class="r" id="dhead"></span><span class="r mcount">Games</span></div><div id="rows"></div>`;
  const draw = () => {
    const era = eras && eras.find(x => x.id === state.g);
    const v = era || {elo: D.teams.map(t => t.elo), matches: D.teams.map(t => t.matches), delta: D.delta, last: D.last};
    const chipList = eras ? [["", "All"], ...eras.map(e => [e.id, e.label])] : [["", "All"], ...[...groups].filter(([k]) => k).sort().map(([k]) => [k, k])];
    const cw = Math.max(...chipList.map(([, l]) => l.length)) * 8 + 24;
    $("chips").innerHTML = chipList
      .map(([k, l]) => `<button class="chip${k === state.g ? " on" : ""}" style="width:${cw}px" data-g="${esc(k)}" title="${esc(groups.get(k) || "")}">${esc(l)}</button>`).join("");
    $("dhead").textContent = `Δ ${v.last}`;
    $("dhead").title = `Rating change during ${v.last}`;
    let list = D.teams.map((t, i) => i);
    if (era) list = list.filter(i => v.matches[i] > 0).sort((a, b) => v.elo[b] - v.elo[a] || a - b);
    const rank = new Map(list.map((i, r) => [i, r + 1]));            // position within the current leaderboard
    if (!eras && state.g) list = list.filter(i => C.group(D.teams[i], i) === state.g);
    const q = state.q.toLowerCase();
    if (q) list = list.filter(i => [D.teams[i].name, ...(D.teams[i].aliases || [])].some(n => n.toLowerCase().includes(q)));
    $("rows").innerHTML = list.map(i => { const t = D.teams[i], dl = v.delta[i], e = v.elo[i], r = rank.get(i);
      return `<div class="row" data-t="${i}"><span class="pos${r <= 3 ? " top" : ""}">${r}</span>${icon(t)}
        <div><div class="name">${esc(t.name)}</div><div class="sub">${esc(C.sub || C.groupLabel(t, i))}${t.note ? " · " + esc(t.note) : ""}</div></div>
        <span class="elo" style="color:${eloColor(e)}">${e}</span>
        <span class="delta ${dl > 0 ? "up" : dl < 0 ? "down" : "flat"}">${dl > 0 ? "+" + dl : dl || "–"}</span><span class="mcount">${v.matches[i]}</span></div>`; }).join("");
  };
  $("chips").onclick = e => { if (e.target.dataset.g !== undefined) { state.g = e.target.dataset.g; draw(); } };
  $("rows").onclick = e => { const r = e.target.closest(".row"); if (r) location.hash = `#${route.comp}/stats/${encodeURIComponent(D.teams[r.dataset.t].name)}`; };
  $("q").oninput = e => { state.q = e.target.value; draw(); };
  draw();
}

// ── history ───────────────────────────────────────────────────────
const teamOptions = sel => `<option value="">All</option>` + D.teams.map((t, i) => `<option value="${i}"${sel === i ? " selected" : ""}>${esc(t.name)}</option>`).join("");
function history() {
  $("view").innerHTML = `<div class="controls"><select id="ht" class="input">${teamOptions()}</select>
    <select id="hp" class="input"><option value="">All periods</option>${[...D.periods].reverse().map(p => `<option>${esc(p)}</option>`).join("")}</select></div><div id="list"></div>`;
  const draw = () => {
    const t = $("ht").value, p = $("hp").value;
    const rows = []; for (let i = D.matches.length - 1; i >= 0 && rows.length < 400; i--) {
      const m = D.matches[i];
      if ((!p || m[0] === p) && (!t || m[2] == t || m[4] == t)) rows.push(m);
    }
    $("list").innerHTML = rows.length ? rows.map(matchRow).join("") : `<div class="empty">NO MATCHES</div>`;
  };
  $("ht").onchange = $("hp").onchange = draw; draw();
}
function score(m) {
  const [, , , ga, , gb, dec, pa, pb] = m;
  return `${ga}–${gb}` + (dec === "pw" ? ` <span class="pill">(pens)</span>` : dec === "pen" ? ` <span class="pill">(${pa}–${pb} p)</span>` : dec === "aet" ? ` <span class="pill">aet</span>` : "");
}
function matchRow(m) {
  const [per, ph, a, ga, b, gb, dec, pa, pb, ea, eb] = m;
  const wa = ga > gb || (ga === gb && pa > pb), wb = gb > ga || (ga === gb && pb > pa);
  // crests sit at the outer ends of the two name columns, so the layout is symmetric whatever the name length
  return `<div class="match"><span class="pill ph">${tagHtml(ph)}</span>${icon(D.teams[a], "sm")}<span class="a${wa ? " win" : ""}">${esc(D.teams[a].name)}</span>
    <span class="sc">${score(m)}</span><span class="b${wb ? " win" : ""}">${esc(D.teams[b].name)}</span>${icon(D.teams[b], "sm")}<span class="d">${esc(per)} · ${ea}/${eb}</span></div>`;
}

// ── stats / compare ───────────────────────────────────────────────
let chart;
function drawChart(canvas, series) {
  if (chart) chart.destroy();
  if (typeof Chart === "undefined") { canvas.replaceWith(Object.assign(document.createElement("p"), {className: "sub", textContent: "Chart library failed to load."})); return; }
  Chart.defaults.font.family = "Barlow, system-ui, sans-serif";
  chart = new Chart(canvas, {type: "line", data: {labels: D.periods, datasets: series.map(s => ({label: s.label, data: D.periods.map(p => s.map[p] ?? null),
    borderColor: s.color, backgroundColor: s.color, spanGaps: true, tension: .25, pointRadius: 2, borderWidth: 2}))},
    options: {interaction: {mode: "index", intersect: false}, scales: {x: {ticks: {color: "#6b675e", maxTicksLimit: 12}, grid: {color: "#e3ded0"}}, y: {ticks: {color: "#6b675e"}, grid: {color: "#e3ded0"}}},
      plugins: {legend: {labels: {color: "#4d4a43"}}}}});
}
const periodElo = i => { const m = {}; D.tl[i].forEach(e => m[e.per] = e.after); return m; };
const periodStats = i => { const s = new Map(); D.tl[i].forEach(e => { const x = s.get(e.per) || {start: e.before, n: 0}; x.end = e.after; x.n++; s.set(e.per, x); }); return s; };
function seasonTable(i) {
  return `<table class="seasons"><tr><th>${C.period.slice(0, -1)}</th><th>Start</th><th>End</th><th>Δ</th><th>Games</th></tr>${[...periodStats(i)].reverse().map(([p, x]) => {
    const d = x.end - x.start; return `<tr><td>${esc(p)}</td><td>${x.start}</td><td>${x.end}</td><td class="${d > 0 ? "up" : d < 0 ? "down" : "flat"}">${d > 0 ? "+" : ""}${d}</td><td>${x.n}</td></tr>`; }).join("")}</table>`;
}
function stats() {
  const cur = D.teams.findIndex(t => t.name === route.team);
  $("view").innerHTML = `<div class="controls"><select id="st" class="input"><option value="">Select…</option>${D.teams.map((t, i) => `<option value="${i}"${i === cur ? " selected" : ""}>${esc(t.name)}</option>`).join("")}</select></div><div id="out"></div>`;
  $("st").onchange = () => { location.hash = `#${route.comp}/stats/${$("st").value === "" ? "" : encodeURIComponent(D.teams[$("st").value].name)}`; };
  if (cur < 0) { $("out").innerHTML = `<div class="empty">SELECT A TEAM TO VIEW ELO PROGRESSION</div>`; return; }
  const t = D.teams[cur];
  $("out").innerHTML = `<div class="card"><h3 style="display:flex;align-items:center;gap:10px">${icon(t)}${esc(t.name)} · ${t.elo} ELO · #${cur + 1}</h3><canvas id="ch" height="110"></canvas>${t.note ? `<p class="sub" style="margin-top:8px">${esc(t.note)}</p>` : ""}</div>
    <div class="card">${seasonTable(cur)}</div><div class="card">${D.tl[cur].slice().reverse().slice(0, 60).map(e => matchRow(D.matches[e.i])).join("")}</div>`;
  drawChart($("ch"), [{label: t.name, map: periodElo(cur), color: "#b3261e"}]);
}
function compare() {
  const a = D.teams.findIndex(t => t.name === route.team.split("~")[0]), b = D.teams.findIndex(t => t.name === route.team.split("~")[1]);
  $("view").innerHTML = `<div class="controls"><select id="ca" class="input">${teamOptions(a)}</select><span class="mono">vs</span><select id="cb" class="input">${teamOptions(b)}</select></div><div id="out"></div>`;
  const go = () => { const x = $("ca").value, y = $("cb").value; location.hash = `#${route.comp}/compare/${x === "" ? "" : encodeURIComponent(D.teams[x].name)}${y === "" ? "" : "~" + encodeURIComponent(D.teams[y].name)}`; };
  $("ca").onchange = $("cb").onchange = go;
  if (a < 0 || b < 0) { $("out").innerHTML = `<div class="empty">SELECT TWO TEAMS TO COMPARE</div>`; return; }
  const h2h = D.tl[a].filter(e => e.opp === b);
  const w = h2h.filter(e => e.gf > e.ga || (e.gf === e.ga && e.pf > e.pa)).length, l = h2h.filter(e => e.gf < e.ga || (e.gf === e.ga && e.pf < e.pa)).length;
  $("out").innerHTML = `<div class="card"><canvas id="ch" height="110"></canvas></div>
    <div class="card"><h3>Head to head</h3><p>${esc(D.teams[a].name)} ${w}W · ${h2h.length - w - l}D · ${l}L vs ${esc(D.teams[b].name)} (${h2h.length} matches)</p></div>
    ${h2h.length ? `<div class="card">${h2h.slice().reverse().map(e => matchRow(D.matches[e.i])).join("")}</div>` : ""}`;
  drawChart($("ch"), [{label: D.teams[a].name, map: periodElo(a), color: "#b3261e"}, {label: D.teams[b].name, map: periodElo(b), color: "#1f4e79"}]);
}

// ── about ─────────────────────────────────────────────────────────
function about() {
  const ph = Object.entries(D.phases).map(([k, p]) => `<li>${tagHtml(k)} K = ${p.k}</li>`).join("");
  $("view").innerHTML = `<div class="grid2">
    <div class="card"><h3>ELO formula</h3><div class="formula">R ← R + K × (S − E)</div><p>E = 1 / (1 + 10^((R_opp − R_self) / 400))</p>
      <p>S: 1 win · 0.5 draw · 0 loss. Everyone starts at 1600.</p></div>
    <div class="card"><h3>K-factors</h3><ul style="list-style:none;padding:0">${ph}</ul></div>
    <div class="card"><h3>Extra time &amp; penalties</h3><ul><li>Score after extra time is used.</li><li>If a match is decided on penalties, the shoot-out winner counts as the winner.</li>
      ${route.comp === "ucl" ? "<li>Two-legged ties: each leg is rated separately.</li>" : ""}${route.comp === "nl" ? "<li>K depends on the division the match is played in (A 24 · B 12 · C 8 · D 4), so a win in a lower division moves the rating less. There is one common ranking for all divisions.</li><li>Quarter-finals: K of Division A. Semi-finals, 3rd place and final: K 32. Promotion/relegation play-offs between two divisions use the K of the lower one. <b>PO</b> in the history marks these promotion/relegation play-offs.</li><li>The Nations League is played every two years (2018/19, 2020/21, 2022/23 …); the years in between have no edition.</li><li>Two-legged ties: each leg is rated separately.</li>" : ""}${route.comp === "pl" || route.comp === "ekstraklasa" ? "<li>League matches only: no extra time or penalties.</li><li>Clubs keep their rating while outside the top flight.</li><li>The era buttons only filter the years: each club has one continuous rating, shown as it stood at the end of that era (games and Δ count that era only).</li>" : ""}</ul></div>
    <div class="card"><h3>Data</h3><ul><li>${D.periods[0]} – ${D.last}, ${D.matches.length.toLocaleString("en")} matches</li>
      ${C.note ? `<li>${C.note}</li>` : ""}<li>Updated daily from ${C.source || `<a href="https://github.com/openfootball" style="color:var(--accent);text-decoration:underline">openfootball</a>, football-data.org and Wikipedia`}</li>
      <li>Renamed / merged teams are listed in <a href="${REPO}/blob/main/data/teams_${route.comp}.json" style="color:var(--accent);text-decoration:underline">teams file</a></li></ul></div></div>`;
}
render();
