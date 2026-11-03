// Three Moves Ago — API Worker.
// Static files in ./public are served by the assets binding; this script only answers /api/*.
// The browser never receives a solution before the case is finished, and never receives future cases.
import { START, legalMoves, fenToBoard } from './engine.js';
import CASES from './cases.js';

const MAX_ATTEMPTS = 5;
const RELEASE_TZ = 'Europe/Bucharest', RELEASE_HOUR = 7;   // new case every day at 07:00 Romania time
const LAUNCH_UTC = Date.UTC(2026, 9, 21);                  // case #1

function tzParts(d) {
  const p = {};
  for (const x of new Intl.DateTimeFormat('en-US', { timeZone: RELEASE_TZ, year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', hourCycle: 'h23' }).formatToParts(d)) p[x.type] = +x.value;
  return p;
}
function todayNo(now = new Date()) {
  const p = tzParts(now);
  let day = Date.UTC(p.year, p.month - 1, p.day);
  if (p.hour < RELEASE_HOUR) day -= 86400000;
  return Math.max(1, Math.round((day - LAUNCH_UTC) / 86400000) + 1);
}
const caseAt = n => CASES[(n - 1) % CASES.length];

function json(data, status = 200, maxAge = 0) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': maxAge ? `public, max-age=${maxAge}` : 'no-store',
      'x-content-type-options': 'nosniff',
    },
  });
}
const bad = (msg, status = 400) => json({ error: msg }, status);

function parseCaseNo(raw, today) {
  if (raw === 'today') return today;
  if (!/^\d{1,5}$/.test(raw || '')) return null;
  const n = +raw;
  return n >= 1 && n <= today ? n : null;
}

// Replays the moves with the real move generator; returns the final board or null if any move is illegal.
function replay(c, moves) {
  let b = c.start ? fenToBoard(c.start) : START, w = true;
  for (const u of moves) {
    if (typeof u !== 'string' || !/^[a-h][1-8][a-h][1-8]$/.test(u)) return null;
    const i = (+u[1] - 1) * 8 + 'abcdefgh'.indexOf(u[0]), j = (+u[3] - 1) * 8 + 'abcdefgh'.indexOf(u[2]);
    const m = legalMoves(b, w).find(m => m[0] === i && m[1] === j);
    if (!m) return null;
    b = m[2]; w = !w;
  }
  return b;
}

async function readJson(request) {
  try { const t = await request.text(); return t.length > 4000 ? null : JSON.parse(t); } catch (e) { return null; }
}

async function handleApi(request, url) {
  const today = todayNo();
  const parts = url.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);

  if (request.method === 'GET' && parts[0] === 'today') return json({ today });

  // Archive list: number + level of every released case.
  if (request.method === 'GET' && parts[0] === 'cases') {
    const cases = [];
    for (let n = 1; n <= today; n++) cases.push({ n, level: caseAt(n).level });
    return json({ today, cases }, 200, 60);
  }

  // One released case, without its solution.
  if (request.method === 'GET' && parts[0] === 'case' && parts.length === 2) {
    const n = parseCaseNo(parts[1], today);
    if (!n) return bad('This case has not been released yet.', 404);
    const c = caseAt(n);
    return json({ n, today, level: c.level, start: c.start || null, target: c.fen, plies: c.uci.length }, 200, parts[1] === 'today' ? 0 : 300);
  }

  // Check one attempt. Reveals the solution only when the case is solved or the last attempt is used.
  if (request.method === 'POST' && parts[0] === 'check') {
    const body = await readJson(request);
    if (!body) return bad('Invalid request.');
    const n = parseCaseNo(String(body.n), today);
    if (!n) return bad('Unknown case.', 404);
    const c = caseAt(n), sol = c.uci;
    const moves = body.moves, attempt = +body.attempt;
    if (!Array.isArray(moves) || moves.length !== sol.length) return bad('Wrong number of moves.');
    if (!Number.isInteger(attempt) || attempt < 1 || attempt > MAX_ATTEMPTS) return bad('Invalid attempt number.');
    const final = replay(c, moves);
    if (!final) return bad('Illegal move.');
    const solved = final === fenToBoard(c.fen);
    const marks = moves.map((u, k) => u === sol[k] ? 'g' : (sol.some((v, m) => v === u && m % 2 === k % 2) ? 'y' : 'x'));
    const reveal = solved || attempt >= MAX_ATTEMPTS;
    return json({ solved, marks, solution: reveal ? { uci: sol, san: c.san } : null });
  }

  // One hint: the solution move at index k.
  if (request.method === 'POST' && parts[0] === 'hint') {
    const body = await readJson(request);
    if (!body) return bad('Invalid request.');
    const n = parseCaseNo(String(body.n), today);
    if (!n) return bad('Unknown case.', 404);
    const c = caseAt(n), k = +body.k;
    if (!Number.isInteger(k) || k < 0 || k >= c.uci.length) return bad('Invalid move index.');
    return json({ k, san: c.san[k] });
  }

  return bad('Not found.', 404);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    // www and the old workers.dev address -> bare domain
    if (url.hostname === 'www.threemovesago.com' || url.hostname.endsWith('.workers.dev')) {
      url.hostname = 'threemovesago.com';
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === '/api' || url.pathname.startsWith('/api/')) {
      try { return await handleApi(request, url); }
      catch (e) { return bad('Server error.', 500); }
    }
    return env.ASSETS.fetch(request);
  },
};

export { todayNo, handleApi };
