// Chess move generator shared with the client (public/index.html). No castling, en passant or promotion: puzzles never need them.
const START = 'RNBQKBNRPPPPPPPP' + '.'.repeat(32) + 'pppppppprnbqkbnr';
const GLYPH = {k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
const NAMES = {k:'king',q:'queen',r:'rook',b:'bishop',n:'knight',p:'pawn'};
const NM = [[1,2],[2,1],[-1,2],[-2,1],[1,-2],[2,-1],[-1,-2],[-2,-1]];
const KM = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]];
const isW = p => p === p.toUpperCase();
const sqName = i => 'abcdefgh'[i % 8] + (Math.floor(i / 8) + 1);
const sqIdx = s => (+s[1] - 1) * 8 + 'abcdefgh'.indexOf(s[0]);

function attacked(b, sq, byW) {
  const f = sq % 8, r = sq >> 3;
  const at = (x, y) => (x >= 0 && x < 8 && y >= 0 && y < 8) ? b[y * 8 + x] : null;
  const own = p => p && p !== '.' && isW(p) === byW;
  for (const [dx, dy] of NM) { const p = at(f + dx, r + dy); if (own(p) && p.toUpperCase() === 'N') return true; }
  for (const [dx, dy] of KM) { const p = at(f + dx, r + dy); if (own(p) && p.toUpperCase() === 'K') return true; }
  const d = byW ? -1 : 1;
  for (const dx of [-1, 1]) { const p = at(f + dx, r + d); if (own(p) && p.toUpperCase() === 'P') return true; }
  for (const [dirs, ps] of [[[[1,0],[-1,0],[0,1],[0,-1]], 'RQ'], [[[1,1],[1,-1],[-1,1],[-1,-1]], 'BQ']]) {
    for (const [dx, dy] of dirs) {
      let x = f + dx, y = r + dy;
      while (x >= 0 && x < 8 && y >= 0 && y < 8) {
        const p = b[y * 8 + x];
        if (p !== '.') { if (isW(p) === byW && ps.includes(p.toUpperCase())) return true; break; }
        x += dx; y += dy;
      }
    }
  }
  return false;
}
function legalMoves(b, w) {
  const out = [];
  for (let i = 0; i < 64; i++) {
    const p = b[i]; if (p === '.' || isW(p) !== w) continue;
    const f = i % 8, r = i >> 3, u = p.toUpperCase();
    const add = j => { const q = b[j]; if (q === '.' || isW(q) !== w) out.push([i, j]); };
    if (u === 'P') {
      const d = w ? 1 : -1, j = i + 8 * d;
      if (j >= 0 && j < 64 && b[j] === '.') {
        out.push([i, j]);
        if ((w && r === 1) || (!w && r === 6)) { if (b[j + 8 * d] === '.') out.push([i, j + 8 * d]); }
      }
      for (const dx of [-1, 1]) {
        const x = f + dx, y = r + d;
        if (x >= 0 && x < 8 && y >= 0 && y < 8) { const q = b[y * 8 + x]; if (q !== '.' && isW(q) !== w) out.push([i, y * 8 + x]); }
      }
    } else if (u === 'N' || u === 'K') {
      for (const [dx, dy] of (u === 'N' ? NM : KM)) { const x = f + dx, y = r + dy; if (x >= 0 && x < 8 && y >= 0 && y < 8) add(y * 8 + x); }
    } else {
      const dirs = [];
      if ('RQ'.includes(u)) dirs.push([1,0],[-1,0],[0,1],[0,-1]);
      if ('BQ'.includes(u)) dirs.push([1,1],[1,-1],[-1,1],[-1,-1]);
      for (const [dx, dy] of dirs) {
        let x = f + dx, y = r + dy;
        while (x >= 0 && x < 8 && y >= 0 && y < 8) {
          const q = b[y * 8 + x];
          if (q === '.') out.push([i, y * 8 + x]); else { if (isW(q) !== w) out.push([i, y * 8 + x]); break; }
          x += dx; y += dy;
        }
      }
    }
  }
  return out.map(([i, j]) => [i, j, apply(b, i, j)]).filter(([i, j, nb]) => !attacked(nb, nb.indexOf(w ? 'K' : 'k'), !w));
}
function apply(b, i, j) { const a = b.split(''); a[j] = a[i]; a[i] = '.'; return a.join(''); }
function san(b, i, j, nb, w) {
  const p = b[i].toUpperCase(), cap = b[j] !== '.';
  let s;
  if (p === 'P') s = (cap ? sqName(i)[0] + 'x' : '') + sqName(j);
  else {
    s = p;
    const others = legalMoves(b, w).filter(([a, c]) => c === j && a !== i && b[a] === b[i]).map(m => m[0]);
    if (others.length) {
      if (others.every(a => a % 8 !== i % 8)) s += sqName(i)[0];
      else if (others.every(a => (a >> 3) !== (i >> 3))) s += sqName(i)[1];
      else s += sqName(i);
    }
    s += (cap ? 'x' : '') + sqName(j);
  }
  if (attacked(nb, nb.indexOf(w ? 'k' : 'K'), w)) s += legalMoves(nb, !w).length ? '+' : '#';
  return s;
}
function fenToBoard(fen) {
  const rows = fen.split('/'); const a = new Array(64).fill('.');
  rows.forEach((row, k) => { const r = 7 - k; let f = 0; for (const ch of row) { if (/\d/.test(ch)) f += +ch; else { a[r * 8 + f] = ch; f++; } } });
  return a.join('');
}

export { START, isW, sqName, sqIdx, attacked, legalMoves, apply, san, fenToBoard };
