"use strict";
const REPO = "https://github.com/enterdesign/footballelo";
const COMPS = {
  ucl: {file: "data/ucl.json", img: "img/ucl.jpg", eyebrow: "UEFA Champions League", noun: "Clubs", period: "Seasons",
        group: t => t.code, groupLabel: t => t.country, first: "1992/93"},
  wc:  {file: "data/wc.json", img: "img/wc.jpg", eyebrow: "FIFA World Cup", noun: "Nations", period: "Editions",
        group: t => t.region, groupLabel: t => t.label, first: "1930"},
};
const TABS = ["ranking", "history", "stats", "compare", "about"];
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const cache = {};
let D, C, T, route = {comp: "", tab: "ranking", team: ""};

async function load(key) {
  if (!cache[key]) {
    const r = await fetch(COMPS[key].file);
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
const icon = t => { const u = route.comp === "wc" ? flagUrl(t) : t.logo || ""; return `<span class="ico">${u ? `<img src="${esc(u)}" alt="" loading="lazy" onerror="this.remove()">` : ""}</span>`; };
const eloColor = e => e >= 1750 ? "#b45309" : e >= 1700 ? "#c2410c" : e >= 1650 ? "#1d4ed8" : e >= 1600 ? "#15803d" : "#dc2626";
const tagHtml = ph => { const p = D.phases[ph]; return `<span class="tag" style="background:${p.color}30;border-color:${p.color};color:var(--text)">${p.label}</span>`; };

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
  $("subtitle").textContent = `${D.periods[0]} – ${D.last} · updated ${(D.meta || "")}`.replace(/ · updated $/, "");
  $("stats").innerHTML = [[D.periods.length, C.period], [D.matches.length.toLocaleString("en"), "Matches"], [D.teams.length, C.noun]]
    .map(([v, l]) => `<div><div class="stat-val">${v}</div><div class="stat-label">${l}</div></div>`).join("");
  $("tabs").innerHTML = TABS.map(t => `<a class="tab${t === route.tab ? " on" : ""}" href="#${route.comp}/${t}">${t}</a>`).join("");
  document.title = `${C.eyebrow} ELO Ranking`;
  ({ranking, history, stats, compare, about})[route.tab]();
}
async function renderHome() {
  document.title = "Football ELO Rankings";
  $("home-cards").innerHTML = (await Promise.all(Object.keys(COMPS).map(async k => {
    const d = await load(k), c = COMPS[k];
    return `<a class="home-card" href="#${k}" style="background-image:url('${c.img}')"><div class="eyebrow">${c.eyebrow}</div>
      <h2>ELO Ranking</h2><div class="subtitle">${d.periods.length} ${c.period.toLowerCase()} · ${d.matches.length.toLocaleString("en")} matches · ${d.teams.length} ${c.noun.toLowerCase()}</div></a>`;
  }))).join("");
}
window.addEventListener("hashchange", render);
window.addEventListener("scroll", () => document.querySelectorAll(".hero-bg").forEach(el => { el.style.transform = `translateY(${Math.round(scrollY * .35)}px)`; }));

// ── ranking ───────────────────────────────────────────────────────
function ranking() {
  const groups = new Map();
  D.teams.forEach(t => groups.set(C.group(t), C.groupLabel(t)));
  const state = {g: "", q: ""};
  $("view").innerHTML = `<div class="controls"><input id="q" class="input" placeholder="Search…" autocomplete="off"></div>
    <div class="chips" id="chips"></div><div class="row head"><span>Pos</span><span></span><span>${C.noun.slice(0, -1)}</span><span class="r">ELO</span><span class="r" title="Rating change during ${esc(D.last)}">Δ ${esc(D.last)}</span><span class="r mcount">Games</span></div><div id="rows"></div>`;
  const draw = () => {
    const chipList = [["", "ALL"], ...[...groups].sort().map(([k]) => [k, k])];
    const cw = Math.max(...chipList.map(([, l]) => l.length)) * 8 + 24;
    $("chips").innerHTML = chipList
      .map(([k, l]) => `<button class="chip${k === state.g ? " on" : ""}" style="width:${cw}px" data-g="${esc(k)}" title="${esc(groups.get(k) || "")}">${esc(l)}</button>`).join("");
    const q = state.q.toLowerCase();
    $("rows").innerHTML = D.teams.map((t, i) => [t, i]).filter(([t]) => (!state.g || C.group(t) === state.g) &&
      (!q || [t.name, ...(t.aliases || [])].some(n => n.toLowerCase().includes(q))))
      .map(([t, i]) => { const dl = D.delta[i];
        return `<div class="row" data-t="${i}"><span class="pos${i < 3 ? " top" : ""}">${i + 1}</span>${icon(t)}
        <div><div class="name">${esc(t.name)}</div><div class="sub">${esc(C.groupLabel(t))}${t.note ? " · " + esc(t.note) : ""}</div></div>
        <span class="elo" style="color:${eloColor(t.elo)}">${t.elo}</span>
        <span class="delta ${dl > 0 ? "up" : dl < 0 ? "down" : "flat"}">${dl > 0 ? "+" + dl : dl || "–"}</span><span class="mcount">${t.matches}</span></div>`; }).join("");
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
  return `${ga}–${gb}` + (dec === "pen" ? ` <span class="pill">(${pa}–${pb} p)</span>` : dec === "aet" ? ` <span class="pill">aet</span>` : "");
}
function matchRow(m) {
  const [per, ph, a, ga, b, gb, dec, pa, pb, ea, eb] = m;
  const wa = ga > gb || (ga === gb && pa > pb), wb = gb > ga || (ga === gb && pb > pa);
  return `<div class="match"><span class="pill ph">${tagHtml(ph)}</span><span class="a${wa ? " win" : ""}">${esc(D.teams[a].name)}</span>
    <span class="sc">${score(m)}</span><span class="${wb ? "win" : ""}">${esc(D.teams[b].name)}</span><span class="d">${esc(per)} · ${ea}/${eb}</span></div>`;
}

// ── stats / compare ───────────────────────────────────────────────
let chart;
function drawChart(canvas, series) {
  if (chart) chart.destroy();
  if (typeof Chart === "undefined") { canvas.replaceWith(Object.assign(document.createElement("p"), {className: "sub", textContent: "Chart library failed to load."})); return; }
  chart = new Chart(canvas, {type: "line", data: {labels: D.periods, datasets: series.map(s => ({label: s.label, data: D.periods.map(p => s.map[p] ?? null),
    borderColor: s.color, backgroundColor: s.color, spanGaps: true, tension: .25, pointRadius: 2, borderWidth: 2}))},
    options: {interaction: {mode: "index", intersect: false}, scales: {x: {ticks: {color: "#6b7488", maxTicksLimit: 12}, grid: {color: "#e2e5ee"}}, y: {ticks: {color: "#6b7488"}, grid: {color: "#e2e5ee"}}},
      plugins: {legend: {labels: {color: "#4a5468"}}}}});
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
  drawChart($("ch"), [{label: t.name, map: periodElo(cur), color: "#d97706"}]);
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
  drawChart($("ch"), [{label: D.teams[a].name, map: periodElo(a), color: "#d97706"}, {label: D.teams[b].name, map: periodElo(b), color: "#2563eb"}]);
}

// ── about ─────────────────────────────────────────────────────────
function about() {
  const ph = Object.entries(D.phases).map(([k, p]) => `<li>${tagHtml(k)} K = ${p.k}</li>`).join("");
  $("view").innerHTML = `<div class="grid2">
    <div class="card"><h3>ELO formula</h3><div class="formula">R ← R + K × (S − E)</div><p>E = 1 / (1 + 10^((R_opp − R_self) / 400))</p>
      <p>S: 1 win · 0.5 draw · 0 loss. Everyone starts at 1600.</p></div>
    <div class="card"><h3>K-factors</h3><ul style="list-style:none;padding:0">${ph}</ul></div>
    <div class="card"><h3>Extra time &amp; penalties</h3><ul><li>Score after extra time is used.</li><li>If a match is decided on penalties, the shoot-out winner counts as the winner.</li>
      <li>Two-legged ties: each leg is rated separately.</li></ul></div>
    <div class="card"><h3>Data</h3><ul><li>${D.periods[0]} – ${D.last}, ${D.matches.length.toLocaleString("en")} matches</li>
      <li>Updated weekly from <a href="https://github.com/openfootball" style="color:var(--accent)">openfootball</a></li>
      <li>Renamed / merged teams are listed in <a href="${REPO}/blob/main/data/teams_${route.comp === "wc" ? "wc" : "ucl"}.json" style="color:var(--accent)">teams file</a></li></ul></div></div>`;
}
render();
