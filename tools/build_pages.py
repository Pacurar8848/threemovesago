"""Builds the static content pages and the shared layout used by the Worker.

Run from the repo root:  python3 tools/build_pages.py
Writes: public/learn/*.html, public/about.html + public/privacy.html footers, src/layout.js
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://threemovesago.com'
about = (ROOT / 'public/about.html').read_text()

# ---- pieces taken from the About page so every page looks the same ----
FONT_HEAD = about[about.index('<link rel="icon"'):about.index('<script type="application/ld+json">')]
STYLE = about[about.index('<style>\n:root'):about.index('</style>', about.index('<style>\n:root')) + 8]
STYLE = STYLE.replace('</style>', '''.bd{width:100%;max-width:340px;display:block;border-radius:6px;box-shadow:0 0 0 1px var(--line)}
.boards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin:16px 0}
.boards figure{margin:0}.boards figcaption{font-size:13px;color:var(--muted);text-align:center;margin-top:4px}
.moves{font-weight:600;font-size:18px}
.list{list-style:none;padding:0;margin:0}.list li{border-bottom:1px solid var(--line);margin:0}
.list a{display:flex;justify-content:space-between;gap:12px;padding:12px 2px;text-decoration:none;color:var(--ink)}
.list small{color:var(--muted)}
.pager{display:flex;justify-content:space-between;margin-top:28px}
footer a{color:var(--muted)}
</style>''')
HEADER = about[about.index('<header>'):about.index('</header>') + 9]
FOOTER = ('<footer><div class="wrap"><a href="/">Play</a> · <a href="/about">FAQ</a> · <a href="/learn/">Learn</a> · '
          '<a href="/cases">All cases</a> · <a href="/privacy">Privacy</a></div></footer>')

def page(title, desc, path, body, og_type='article', jsonld=None):
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n' if jsonld else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}{path}">
<meta name="theme-color" content="#2d6a4f">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{BASE}/og.png">
<meta name="twitter:card" content="summary_large_image">
{FONT_HEAD}{ld}{STYLE}
</head>
<body>
{HEADER}
<main class="wrap">
{body}
</main>
{FOOTER}
</body>
</html>
'''

GLYPH = {'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'}
def board(fen, label):
    rows = fen.split('/'); cells = []
    for k, row in enumerate(rows):
        x = 0
        for ch in row:
            if ch.isdigit(): x += int(ch); continue
            cells.append((x, k, ch)); x += 1
    sq = ''.join(f'<rect x="{f}" y="{r}" width="1" height="1" fill="{"#e9ebe2" if (f + r) % 2 == 0 else "#95ab9e"}"/>' for r in range(8) for f in range(8))
    pcs = ''.join(f'<text x="{x + .5}" y="{y + .56}" class="{"w" if p.isupper() else "b"}">{GLYPH[p.lower()]}&#xFE0E;</text>' for x, y, p in cells)
    return (f'<svg class="bd" viewBox="0 0 8 8" role="img" aria-label="{label}"><style>text{{font-size:.82px;text-anchor:middle;dominant-baseline:middle;font-family:"DejaVu Sans","Segoe UI Symbol","Apple Symbols",serif}}'
            f'.w{{fill:#fffdf7;stroke:#151614;stroke-width:.03px}}.b{{fill:#151614}}</style>{sq}{pcs}</svg>')

START = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
EX1 = 'rnbqkbnr/ppp1pppp/8/8/8/2N5/PPPP1PPP/R1BQKBNR'      # 1.e4 d5 2.exd5 Qxd5 3.Nc3 Qd8
EX2 = 'rnbq2nr/pppp1kpp/8/2b1p3/4P3/8/PPPP1PPP/RNBQK1NR'    # 1.e4 e5 2.Bc4 Bc5 3.Bxf7+ Kxf7
def boards(*items):
    return '<div class="boards">' + ''.join(f'<figure>{board(f, c)}<figcaption>{c}</figcaption></figure>' for f, c in items) + '</div>'
CTA = '<div class="cta"><a class="play" href="/">Play today’s case</a></div>'

def article(title, h1, desc, path, body):
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc,
          "url": BASE + path, "image": BASE + "/og.png", "inLanguage": "en",
          "publisher": {"@type": "Organization", "name": "Three Moves Ago"}}
    return page(title, desc, path, f'<h1>{h1}</h1>\n{body}\n{CTA}', 'article', ld)

LEARN = {
'retrograde-analysis': article(
 'Retrograde Analysis in Chess: How to Reason Backwards – Three Moves Ago',
 'Retrograde analysis: reasoning backwards in chess',
 'What retrograde analysis is, the clues retro solvers use (material, pawns, kings, checks) and a worked example you can solve in a minute.',
 '/learn/retrograde-analysis', f'''
<p class="lead">Most chess thinking goes forwards: what is the best move now? Retrograde analysis goes the other way. You look at a position and ask what must already have happened.</p>
<h2>The idea</h2>
<p>Every chess position is the end of a story. Pieces cannot jump, pawns never move backwards, and a captured piece is gone for good. Because the rules are so strict, a position often contains enough evidence to rebuild part of the game that produced it. Working that out is called <b>retrograde analysis</b>, or <b>retro analysis</b> for short.</p>
<p>It is a long-standing branch of chess problem composition. It reached a wide audience through the logician Raymond Smullyan, whose book <i>The Chess Mysteries of Sherlock Holmes</i> turns retro problems into detective stories.</p>
<h2>The clues a retro solver looks for</h2>
<ul>
<li><b>Material.</b> Count the pieces. Every missing piece was captured, and every capture was made by a piece of the other colour.</li>
<li><b>Pawn files.</b> A pawn can only change file by capturing. A pawn on the wrong file, or two pawns on the same file, proves a capture happened.</li>
<li><b>Pieces that cannot have left.</b> A bishop behind its own unmoved pawns has never moved. A rook in the corner with its king beside it may never have moved either.</li>
<li><b>Kings.</b> A king away from its home square must have walked there, one square per move, and only through squares that were not attacked at the time.</li>
<li><b>Checks.</b> Only one side can be in check, and a check must have been given by the last move. This often fixes the order of moves.</li>
<li><b>Tempo.</b> If one side needed fewer moves than it had, the extra moves were spent somewhere. A piece that went out and came back is a classic answer.</li>
</ul>
<h2>A small example</h2>
<p>White and Black have each played three moves from the starting position, and this is the result:</p>
{boards((START, 'Start'), (EX1, 'After three moves each'))}
<p>White is missing the e-pawn and has a knight on c3. Black is missing the d-pawn, and at first sight Black’s other pieces have not moved at all. But Black played three moves, so something did move. The d-pawn must have gone to d5, and the white e-pawn must have taken it there. Then who took the white pawn on d5? Only the queen could reach it, and it has since gone home.</p>
<p class="moves">1. e4 d5 2. exd5 Qxd5 3. Nc3 Qd8</p>
<p>The queen on d8 looks as if it never moved, but it left, captured, and returned. That is the core trick of retro chess: the position hides moves that left no visible trace.</p>
<h2>Try it every day</h2>
<p><a href="/">Three Moves Ago</a> gives you a new retro puzzle every day: a target position and the job of finding the three moves each side played to reach it.</p>
'''),
'proof-games': article(
 'What Is a Proof Game in Chess? Shortest Proof Games Explained – Three Moves Ago',
 'What is a proof game?',
 'A proof game is a chess problem where you must find the exact game that reaches a given position. Here is how they work, why they need a unique solution, and an example.',
 '/learn/proof-games', f'''
<p class="lead">A proof game asks a simple question: here is a position, now show me a legal game that reaches it.</p>
<h2>The rules of the genre</h2>
<p>In a proof game you are given a final position and a number of moves. You must find a game, starting from the normal opening position, that reaches exactly that position in exactly that many moves. When the number of moves is the smallest possible, the problem is called a <b>shortest proof game</b> (often written SPG).</p>
<p>A well-made proof game has <b>one solution only</b>. That is what turns it from a puzzle into a proof: every move is forced by the evidence on the board, and no other order works.</p>
<h2>Why they are harder than they look</h2>
<ul>
<li>The moves do not have to be good. Pieces get captured for no reason, kings walk into the open, and queens are given away.</li>
<li>The obvious explanation is often wrong. A missing piece might not have been taken by the piece that seems to be standing on its square.</li>
<li>Some moves leave no trace. A piece can move out, capture something and return, so the final position shows only the missing victim.</li>
<li>The move count is strict. With three moves each, one wasted move ruins the whole sequence.</li>
</ul>
<h2>An example</h2>
<p>Three moves each, from the opening position, reach this:</p>
{boards((START, 'Start'), (EX2, 'Target'))}
<p>Black’s king stands on f7, Black’s f-pawn is gone, and White has lost the light-squared bishop. Black needed two of its three moves for e5 and Bc5, so the f-pawn never moved: it was captured on f7, and the king then took the piece that captured it. The missing bishop is the only white piece that could have reached f7 in time:</p>
<p class="moves">1. e4 e5 2. Bc4 Bc5 3. Bxf7+ Kxf7</p>
<h2>Proof games every day</h2>
<p>Every case on <a href="/">Three Moves Ago</a> is a short proof game: three moves for White, three for Black, one solution. Some start from the opening position, and the harder ones start from a real middlegame.</p>
'''),
'how-to-solve': article(
 'How to Solve Retro Chess Puzzles: A Step-by-Step Method – Three Moves Ago',
 'How to solve retro chess puzzles',
 'A practical step-by-step method for solving retro chess puzzles and short proof games: compare the positions, count captures, find the hidden moves, and use the feedback.',
 '/learn/how-to-solve', f'''
<p class="lead">You do not need to be a strong player to solve retro puzzles. You need to be a careful detective. This is the method that works best on Three Moves Ago.</p>
<h2>1. Compare the two positions square by square</h2>
<p>Write down what is different between the start and the target: which pieces moved, which squares are now empty, which are newly occupied. Each side has exactly three moves, so this list is your budget.</p>
<h2>2. Account for every missing piece</h2>
<p>A piece that disappeared was captured. Ask which enemy piece could have reached that square, and on which move. Captures by pawns are the easiest to spot, because the pawn ends up on a new file.</p>
<h2>3. Count the moves you can see</h2>
<p>If White clearly needs two moves for the visible changes, there is one move left to explain. Missing moves usually hide in one of three places: a piece that went out and came back, a capture made by a piece that then moved on, or a piece that took a longer route than you expected.</p>
<h2>4. Look for checks and forced replies</h2>
<p>If a king has moved, ask why. A check is often the reason, and it tells you the order: the check came first, and the king move was the reply.</p>
<h2>5. Play it out and read the colours</h2>
<p>Enter your six moves. Each move gets a colour:</p>
<div class="card">
<p style="margin:0 0 6px"><span class="tile g">Nf3</span>Right move at the right turn: keep it.</p>
<p style="margin:0 0 6px"><span class="tile y">Bxf7</span>Right move, wrong turn: it belongs somewhere else in the sequence.</p>
<p style="margin:0"><span class="tile x">a3</span>Not in the solution: replace it.</p>
</div>
<p>Yellow tiles are the most useful clue. They mean you found a real move but the order is wrong, which is usually about checks or about which piece had to move first.</p>
<h2>6. Save the hint for the hard part</h2>
<p>You get one hint per case. It reveals the first move of the solution that you have not yet got right, so it is most valuable after an attempt or two, once you know which part of the story you are missing.</p>
<h2>Common traps</h2>
<ul>
<li>Thinking a piece on its home square never moved.</li>
<li>Assuming the piece standing on a square is the one that made the capture there.</li>
<li>Playing sensible chess moves. The solution often contains moves no player would choose.</li>
</ul>
'''),
}

LEARN_INDEX = page('Learn Retro Chess: Retrograde Analysis & Proof Games – Three Moves Ago',
  'Short guides to retro chess: what retrograde analysis and proof games are, and a step-by-step method for solving them.',
  '/learn/', '''<h1>Learn retro chess</h1>
<p class="lead">Short guides for solving puzzles where you work backwards from a position.</p>
<ul class="list">
<li><a href="/learn/retrograde-analysis"><span><b>Retrograde analysis</b><br><small>What it is and the clues retro solvers use</small></span><span>→</span></a></li>
<li><a href="/learn/proof-games"><span><b>Proof games</b><br><small>Find the exact game that reaches a position</small></span><span>→</span></a></li>
<li><a href="/learn/how-to-solve"><span><b>How to solve retro puzzles</b><br><small>A step-by-step method, plus common traps</small></span><span>→</span></a></li>
</ul>
''' + CTA, 'website')

out = ROOT / 'public/learn'; out.mkdir(exist_ok=True)
for slug, html in LEARN.items(): (out / f'{slug}.html').write_text(html)
(out / 'index.html').write_text(LEARN_INDEX)

# common footer on the existing hand-written pages (and remove a duplicated CTA)
for name in ('about.html', 'privacy.html'):
    p = ROOT / 'public' / name; s = p.read_text()
    s = re.sub(r'<footer>.*?</footer>', FOOTER, s, flags=re.S)
    s = s.replace(CTA + '\n' + CTA, CTA)
    p.write_text(s)

# layout for the Worker-rendered pages (case pages, case list)
(ROOT / 'src/layout.js').write_text(
    '// Generated by tools/build_pages.py — shared layout for pages rendered by the Worker.\n'
    f'export const HEAD = {json.dumps(FONT_HEAD + STYLE)};\n'
    f'export const HEADER = {json.dumps(HEADER)};\n'
    f'export const FOOTER = {json.dumps(FOOTER)};\n')
print('ok')
