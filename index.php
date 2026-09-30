<?php
function readJson($path) {
    if (!file_exists($path)) return [];
    $data = json_decode(file_get_contents($path), true);
    return is_array($data) ? $data : [];
}

$uclMatches   = readJson(__DIR__ . '/ucl/matches.json');
$uclMatchCount = count($uclMatches);
$uclSeasons    = count(array_unique(array_column($uclMatches, 'season')));
$uclTeams      = count(array_unique(array_merge(
    array_column($uclMatches, 'teamA'),
    array_column($uclMatches, 'teamB')
)));

$wcMatches    = readJson(__DIR__ . '/worldcup/wc_matches.json');
$wcMatchCount  = count($wcMatches);
$wcEditions    = count(array_unique(array_column($wcMatches, 'year')));
$wcTeams       = count(array_unique(array_merge(
    array_column($wcMatches, 'teamA'),
    array_column($wcMatches, 'teamB')
)));

function fmt($n) { return number_format($n, 0, '.', ','); }
?><!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Football ELO Rankings</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Bebas+Neue&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --gold: #f5c842;
      --blue: #5ab4ff;
      --dark: #06070c;
    }

    body {
      font-family: 'DM Mono', monospace;
      background: var(--dark);
      color: #f0f4ff;
      overflow-x: hidden;
    }

    /* ── FULL-SCREEN HERO ── */
    .hero {
      position: relative;
      width: 100%;
      height: 100vh;
      min-height: 600px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .parallax-bg {
      position: absolute;
      inset: -20% 0;
      background: url('1soccer-sport-environment-filed.jpg') center 30% / cover no-repeat;
      will-change: transform;
      z-index: 0;
    }

    .hero-overlay {
      position: absolute; inset: 0; z-index: 1;
      background:
        linear-gradient(to bottom, rgba(6,7,12,0.6) 0%, rgba(6,7,12,0.08) 40%, rgba(6,7,12,0.75) 100%),
        linear-gradient(to right, rgba(6,7,12,0.85) 0%, rgba(6,7,12,0.08) 28%, rgba(6,7,12,0.08) 72%, rgba(6,7,12,0.85) 100%);
    }
    .hero-vignette {
      position: absolute; inset: 0; z-index: 2;
      background: radial-gradient(ellipse 90% 80% at 50% 50%, transparent 35%, rgba(6,7,12,0.65) 100%);
      pointer-events: none;
    }
    .hero-scanlines {
      position: absolute; inset: 0; z-index: 3;
      background-image: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.04) 3px, rgba(0,0,0,0.04) 4px);
      pointer-events: none;
    }

    .corner {
      position: absolute; z-index: 5;
      width: 50px; height: 50px; pointer-events: none;
    }
    .corner--tl { top: 24px; left: 24px; border-top: 1px solid rgba(255,255,255,0.18); border-left: 1px solid rgba(255,255,255,0.18); }
    .corner--tr { top: 24px; right: 24px; border-top: 1px solid rgba(255,255,255,0.18); border-right: 1px solid rgba(255,255,255,0.18); }
    .corner--bl { bottom: 24px; left: 24px; border-bottom: 1px solid rgba(255,255,255,0.18); border-left: 1px solid rgba(255,255,255,0.18); }
    .corner--br { bottom: 24px; right: 24px; border-bottom: 1px solid rgba(255,255,255,0.18); border-right: 1px solid rgba(255,255,255,0.18); }

    /* ── 3-COLUMN LAYOUT ── */
    .hero-layout {
      position: relative; z-index: 10;
      width: 100%; max-width: 1260px;
      padding: 0 32px;
      display: grid;
      grid-template-columns: 280px 1fr 280px;
      align-items: center;
      gap: 28px;
    }

    /* ── CENTRE ── */
    .hero-centre {
      text-align: center;
      display: flex; flex-direction: column; align-items: center;
      animation: fadeUp 1s .1s cubic-bezier(.22,1,.36,1) both;
    }

    .eyebrow {
      font-size: 9px; letter-spacing: 5px; text-transform: uppercase;
      color: rgba(255,255,255,0.35); margin-bottom: 16px;
    }
    .eyebrow::before, .eyebrow::after {
      content: ""; display: inline-block;
      width: 22px; height: 1px;
      background: var(--gold); opacity: 0.6; vertical-align: middle;
    }
    .eyebrow::before { margin-right: 12px; }
    .eyebrow::after  { margin-left:  12px; }

    h1 {
      font-family: 'Bebas Neue', sans-serif;
      font-size: clamp(58px, 8vw, 108px);
      letter-spacing: 8px; line-height: 0.88;
      color: #fff;
      text-shadow: 0 4px 40px rgba(0,0,0,0.6);
    }
    h1 .accent {
      color: var(--gold);
      text-shadow: 0 0 50px rgba(245,200,66,0.45), 0 2px 0 rgba(0,0,0,0.5);
    }

    .tagline {
      font-size: 9px; letter-spacing: 3px; text-transform: uppercase;
      color: rgba(255,255,255,0.28); margin-top: 18px;
    }

    /* ── SIDE CARDS ── */
    .card {
      display: block; text-decoration: none;
      position: relative; border-radius: 6px;
      padding: 26px 22px; overflow: hidden;
      background: rgba(6,7,12,0.65);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
      border: 1px solid rgba(255,255,255,0.08);
      transition: transform .25s cubic-bezier(.22,1,.36,1), border-color .25s, box-shadow .25s;
    }
    .card::before {
      content: "";
      position: absolute; inset: 0; border-radius: 6px;
      background: linear-gradient(145deg, rgba(255,255,255,0.05) 0%, transparent 60%);
      pointer-events: none;
    }
    .card::after {
      content: ""; position: absolute;
      width: 160px; height: 160px; border-radius: 50%;
      top: -40px; right: -40px; pointer-events: none;
      opacity: 0; transition: opacity .4s; filter: blur(50px);
    }
    .card.ucl::after { background: rgba(245,200,66,0.22); }
    .card.wc::after  { background: rgba(90,180,255,0.18); }

    .card:hover { transform: translateY(-4px) scale(1.01); }
    .card:hover::after { opacity: 1; }
    .card.ucl:hover { border-color: rgba(245,200,66,0.35); box-shadow: 0 20px 60px rgba(245,200,66,0.1); }
    .card.wc:hover  { border-color: rgba(90,180,255,0.35);  box-shadow: 0 20px 60px rgba(90,180,255,0.1); }

    .card-left  { animation: slideRight .9s .3s cubic-bezier(.22,1,.36,1) both; }
    .card-right { animation: slideLeft  .9s .4s cubic-bezier(.22,1,.36,1) both; }

    @keyframes slideRight { from { opacity:0; transform: translateX(-40px); } to { opacity:1; transform: translateX(0); } }
    @keyframes slideLeft  { from { opacity:0; transform: translateX( 40px); } to { opacity:1; transform: translateX(0); } }
    @keyframes fadeUp     { from { opacity:0; transform: translateY(28px);  } to { opacity:1; transform: translateY(0);  } }

    .card-arrow {
      position: absolute; top: 20px; right: 20px;
      font-size: 13px; font-family: 'DM Mono', monospace;
      color: rgba(255,255,255,0.15);
      transition: color .2s, transform .2s;
    }
    .card:hover .card-arrow { transform: translate(2px,-2px); }
    .card.ucl:hover .card-arrow { color: var(--gold); }
    .card.wc:hover  .card-arrow { color: var(--blue); }

    .card-icon { font-size: 28px; margin-bottom: 12px; }

    .card-tag {
      font-size: 8px; letter-spacing: 3px; text-transform: uppercase; margin-bottom: 6px;
    }
    .card.ucl .card-tag { color: var(--gold); }
    .card.wc  .card-tag { color: var(--blue); }

    .card-title {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 23px; letter-spacing: 2px; color: #fff; line-height: 1; margin-bottom: 10px;
    }

    .card-desc {
      font-size: 9px; color: rgba(255,255,255,0.30); line-height: 1.85;
    }

    .card-divider { height: 1px; background: rgba(255,255,255,0.06); margin: 14px 0; }

    .card-stats { display: flex; }
    .card-stat {
      flex: 1; text-align: center;
      border-right: 1px solid rgba(255,255,255,0.05); padding: 0 6px;
    }
    .card-stat:last-child { border-right: none; }

    .card-stat-val {
      font-family: 'Bebas Neue', sans-serif;
      font-size: 21px; letter-spacing: 1px; display: block; line-height: 1;
    }
    .card.ucl .card-stat-val { color: var(--gold); }
    .card.wc  .card-stat-val { color: var(--blue); }

    .card-stat-label {
      font-size: 7px; letter-spacing: 1.5px; text-transform: uppercase;
      color: rgba(255,255,255,0.22); margin-top: 3px; display: block;
    }

    .footer {
      background: var(--dark); text-align: center; padding: 20px;
      border-top: 1px solid rgba(255,255,255,0.04);
    }
    .footer p {
      font-size: 8px; letter-spacing: 2px; text-transform: uppercase;
      color: rgba(255,255,255,0.1);
    }

    /* ── RESPONSIVE ── */
    @media (max-width: 900px) {
      .hero { height: auto; min-height: 100vh; padding: 70px 0 60px; }
      .hero-layout {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto;
        gap: 20px; padding: 24px 20px;
        justify-items: center;
      }
      /* On mobile put title first */
      .card-left  { order: 2; width: 100%; max-width: 340px; }
      .hero-centre { order: 1; }
      .card-right { order: 3; width: 100%; max-width: 340px; }
      h1 { font-size: 72px; }
    }
  </style>
</head>
<body>

<section class="hero" id="hero">
  <div class="parallax-bg" id="parallaxBg"></div>
  <div class="hero-overlay"></div>
  <div class="hero-vignette"></div>
  <div class="hero-scanlines"></div>

  <div class="corner corner--tl"></div>
  <div class="corner corner--tr"></div>
  <div class="corner corner--bl"></div>
  <div class="corner corner--br"></div>

  <div class="hero-layout">

    <!-- LEFT: UCL -->
    <a class="card ucl card-left" href="ucl/">
      <span class="card-arrow">↗</span>
      <div class="card-icon">🏆</div>
      <div class="card-tag">Club Football</div>
      <div class="card-title">UEFA Champions League</div>
      <div class="card-desc">ELO rankings for all clubs in the Champions League era, from 1992/93 to present.</div>
      <div class="card-divider"></div>
      <div class="card-stats">
        <div class="card-stat">
          <span class="card-stat-val"><?= $uclSeasons ?></span>
          <span class="card-stat-label">Seasons</span>
        </div>
        <div class="card-stat">
          <span class="card-stat-val"><?= fmt($uclMatchCount) ?></span>
          <span class="card-stat-label">Matches</span>
        </div>
        <div class="card-stat">
          <span class="card-stat-val"><?= $uclTeams ?></span>
          <span class="card-stat-label">Clubs</span>
        </div>
      </div>
    </a>

    <!-- CENTRE TITLE -->
    <div class="hero-centre">
      <div class="eyebrow">Football Analytics</div>
      <h1>ELO<br><span class="accent">Rankings</span></h1>
      <div class="tagline">Historical · Data-Driven · Club &amp; International</div>
    </div>

    <!-- RIGHT: World Cup -->
    <a class="card wc card-right" href="worldcup/">
      <span class="card-arrow">↗</span>
      <div class="card-icon">🌍</div>
      <div class="card-tag">International Football</div>
      <div class="card-title">FIFA World Cup</div>
      <div class="card-desc">ELO rankings for all national teams in the World Cup, from the first edition in 1930.</div>
      <div class="card-divider"></div>
      <div class="card-stats">
        <div class="card-stat">
          <span class="card-stat-val"><?= $wcEditions ?></span>
          <span class="card-stat-label">Editions</span>
        </div>
        <div class="card-stat">
          <span class="card-stat-val"><?= fmt($wcMatchCount) ?></span>
          <span class="card-stat-label">Matches</span>
        </div>
        <div class="card-stat">
          <span class="card-stat-val"><?= $wcTeams ?></span>
          <span class="card-stat-label">Teams</span>
        </div>
      </div>
    </a>

  </div>
</section>

<div class="footer">
  <p>Football ELO Rankings &mdash; Data-Driven Historical Analysis</p>
</div>

<script>
  const bg = document.getElementById('parallaxBg');
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        bg.style.transform = `translateY(${window.scrollY * 0.4}px)`;
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
</script>

</body>
</html>
