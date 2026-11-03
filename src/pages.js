// Server-rendered pages: one page per released case, the case list, and the sitemap.
// Solutions are never included.
import { HEAD, HEADER, FOOTER } from './layout.js';

const BASE = 'https://threemovesago.com';
const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR';
const OPENING_NAMES = {
  italian: 'the Italian Game', twoknights: 'the Two Knights Defence', ruy: 'the Ruy Lopez', berlin: 'the Berlin Defence',
  scotch: 'the Scotch Game', petrov: 'the Petrov Defence', najdorf: 'the Sicilian Najdorf', dragon: 'the Sicilian Dragon',
  taimanov: 'the Sicilian Taimanov', sveshnikov: 'the Sicilian Sveshnikov', alapin: 'the Alapin Sicilian', rossolimo: 'the Rossolimo Sicilian',
  morra: 'the Smith-Morra Gambit', winawer: 'the French Winawer', tarrasch: 'the French Tarrasch', frenchadv: 'the French Advance',
  french: 'the French Defence', carokann: 'the Caro-Kann', caroadv: 'the Caro-Kann Advance', scandi: 'the Scandinavian Defence',
  pirc: 'the Pirc Defence', alekhine: 'Alekhine’s Defence', philidor: 'the Philidor Defence', evans: 'the Evans Gambit',
  vienna: 'the Vienna Game', qgd: 'the Queen’s Gambit Declined', qgdx: 'the Exchange Queen’s Gambit Declined', slav: 'the Slav Defence',
  meran: 'the Semi-Slav Meran', qga: 'the Queen’s Gambit Accepted', catalan: 'the Catalan', nimzo: 'the Nimzo-Indian',
  qid: 'the Queen’s Indian', kid: 'the King’s Indian', grunfeld: 'the Grünfeld', benoni: 'the Modern Benoni', benko: 'the Benko Gambit',
  stonewall: 'the Stonewall Dutch', london: 'the London System', colle: 'the Colle System', english: 'the English Opening',
  englishrev: 'the Reversed Sicilian', reti: 'the Réti Opening', kia: 'the King’s Indian Attack', modern: 'the Modern Defence',
};
const NAMES = { q: 'queen', r: 'rook', b: 'bishop', n: 'knight', p: 'pawn' };
const GLYPH = { k: '♚', q: '♛', r: '♜', b: '♝', n: '♞', p: '♟' };

const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
const fmtDate = (n, launchUtc) => new Date(launchUtc + (n - 1) * 86400000).toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
const isoDate = (n, launchUtc) => new Date(launchUtc + (n - 1) * 86400000).toISOString().slice(0, 10);

function board(fen, label) {
  let sq = '', pcs = '';
  for (let r = 0; r < 8; r++) for (let f = 0; f < 8; f++) sq += `<rect x="${f}" y="${r}" width="1" height="1" fill="${(f + r) % 2 ? '#95ab9e' : '#e9ebe2'}"/>`;
  fen.split('/').forEach((row, y) => { let x = 0; for (const ch of row) { if (/\d/.test(ch)) { x += +ch; continue; } pcs += `<text x="${x + .5}" y="${y + .56}" class="${ch === ch.toUpperCase() ? 'w' : 'b'}">${GLYPH[ch.toLowerCase()]}&#xFE0E;</text>`; x++; } });
  return `<svg class="bd" viewBox="0 0 8 8" role="img" aria-label="${esc(label)}"><style>text{font-size:.82px;text-anchor:middle;dominant-baseline:middle;font-family:"DejaVu Sans","Segoe UI Symbol","Apple Symbols",serif}.w{fill:#fffdf7;stroke:#151614;stroke-width:.03px}.b{fill:#151614}</style>${sq}${pcs}</svg>`;
}
function count(fen) { const c = {}; for (const ch of fen) if (/[a-zA-Z]/.test(ch)) c[ch] = (c[ch] || 0) + 1; return c; }
function missing(startFen, targetFen, white) {
  const a = count(startFen), b = count(targetFen), out = [];
  for (const p of 'qrbnp') { const k = white ? p.toUpperCase() : p, d = (a[k] || 0) - (b[k] || 0); if (d > 0) out.push(`${d} ${NAMES[p]}${d > 1 ? 's' : ''}`); }
  return out.length ? out.join(', ') : 'nothing';
}

function layout({ title, desc, path, body, jsonld }) {
  const ld = jsonld ? `<script type="application/ld+json">${JSON.stringify(jsonld)}</script>\n` : '';
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${BASE}${path}">
<meta name="theme-color" content="#2d6a4f">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="${BASE}${path}">
<meta property="og:image" content="${BASE}/og.png">
<meta name="twitter:card" content="summary_large_image">
${HEAD}${ld}
</head>
<body>
${HEADER}
<main class="wrap">
${body}
</main>
${FOOTER}
</body>
</html>`;
}
const html = (body, status = 200, maxAge = 600) => new Response(body, { status, headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': `public, max-age=${maxAge}` } });

export function casePage(n, c, today, launchUtc) {
  const level = c.level, mid = !!c.start, start = c.start || START_FEN;
  const opening = mid && OPENING_NAMES[c.opening] ? OPENING_NAMES[c.opening] : null;
  const date = fmtDate(n, launchUtc);
  const title = `Case #${n} – ${level} Retro Chess Puzzle – Three Moves Ago`;
  const desc = `Daily retro chess puzzle #${n} (${level}${opening ? ', after ' + opening : ''}): find the 3 moves by White and 3 by Black that reach the target position.`;
  const intro = mid
    ? `This case starts from a real middlegame${opening ? ` that arose from ${opening}` : ''}, with White to move. Find the three moves by White and the three moves by Black that turn the start position into the target.`
    : 'This case starts from the normal opening position. Find the three moves by White and the three moves by Black that lead to the target.';
  const body = `<p class="lead" style="font-size:15px;margin:0 0 6px">${esc(date)}</p>
<h1>Case #${n} · ${esc(level)}</h1>
<p>${esc(intro)}</p>
<div class="boards">${mid ? `<figure>${board(start, 'Start position')}<figcaption>Start</figcaption></figure>` : ''}<figure>${board(c.fen, 'Target position')}<figcaption>Target</figcaption></figure></div>
<div class="card"><b>Clues on the board</b><br>White has lost: ${missing(start, c.fen, true)}.<br>Black has lost: ${missing(start, c.fen, false)}.<br>Every missing piece was captured during these six moves.</div>
<div class="cta"><a class="play" href="/?case=${n}">Play Case #${n}</a></div>
<div class="pager">${n > 1 ? `<a href="/case/${n - 1}">← Case #${n - 1}</a>` : '<span></span>'}${n < today ? `<a href="/case/${n + 1}">Case #${n + 1} →</a>` : '<a href="/cases">All cases</a>'}</div>`;
  const jsonld = { '@context': 'https://schema.org', '@type': 'WebPage', name: `Case #${n} · ${level}`, description: desc, url: `${BASE}/case/${n}`, datePublished: isoDate(n, launchUtc), isPartOf: { '@type': 'WebSite', name: 'Three Moves Ago', url: BASE + '/' } };
  return html(layout({ title, desc, path: `/case/${n}`, body, jsonld }), 200, n === today ? 300 : 3600);
}

export function listPage(today, caseAt, launchUtc) {
  let items = '';
  for (let n = today; n >= 1; n--) items += `<li><a href="/case/${n}"><span><b>Case #${n}</b><br><small>${esc(fmtDate(n, launchUtc))}</small></span><small>${esc(caseAt(n).level)}</small></a></li>`;
  const body = `<h1>All cases</h1>
<p class="lead">Every daily retro chess puzzle so far. Each one is a short proof game: three moves for White, three for Black, one solution.</p>
<ul class="list">${items}</ul>`;
  return html(layout({ title: 'All Cases – Daily Retro Chess Puzzles – Three Moves Ago', desc: `All ${today} daily retro chess puzzles from Three Moves Ago. Find the moves that led to each position.`, path: '/cases', body }), 200, 300);
}

export function sitemap(today, launchUtc) {
  const urls = [['/', 'daily', '1.0'], ['/learn/', 'monthly', '0.8'], ['/learn/retrograde-analysis', 'monthly', '0.8'], ['/learn/proof-games', 'monthly', '0.8'],
    ['/learn/how-to-solve', 'monthly', '0.8'], ['/about', 'monthly', '0.6'], ['/cases', 'daily', '0.6'], ['/privacy', 'yearly', '0.2']];
  for (let n = today; n >= 1; n--) urls.push([`/case/${n}`, n === today ? 'daily' : 'yearly', '0.5', isoDate(n, launchUtc)]);
  const body = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls.map(([p, f, pr, lm]) => `  <url><loc>${BASE}${p}</loc>${lm ? `<lastmod>${lm}</lastmod>` : ''}<changefreq>${f}</changefreq><priority>${pr}</priority></url>`).join('\n') + '\n</urlset>\n';
  return new Response(body, { headers: { 'content-type': 'application/xml; charset=utf-8', 'cache-control': 'public, max-age=3600' } });
}

export function notFound() {
  return html(layout({ title: 'Not found – Three Moves Ago', desc: 'This page does not exist, or this case has not been released yet.', path: '/404',
    body: '<h1>Not here yet</h1><p>This page does not exist, or this case has not been released yet. A new case comes out every day at 07:00 Romania time.</p><div class="cta"><a class="play" href="/">Play today’s case</a></div>' }), 404, 60);
}
