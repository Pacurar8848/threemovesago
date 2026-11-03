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

def page(title, desc, path, body, og_type='article', jsonld=None, lang='en', alternates=None):
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n' if jsonld else ''
    alt = ''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE}{u}">\n' for l, u in (alternates or []))
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}{path}">
{alt}<meta name="theme-color" content="#2d6a4f">
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

def article(title, h1, desc, path, body, faq=None, lang='en', alternates=None, crumbs=('Learn', '/learn/'), cta=None):
    graph = [{"@type": "Article", "headline": h1, "description": desc, "url": BASE + path, "image": BASE + "/og.png",
              "inLanguage": lang, "datePublished": "2026-11-03", "dateModified": "2026-11-03",
              "author": {"@type": "Organization", "name": "Three Moves Ago", "url": BASE + "/"},
              "publisher": {"@type": "Organization", "name": "Three Moves Ago", "logo": {"@type": "ImageObject", "url": BASE + "/apple-touch-icon.png"}}},
             {"@type": "BreadcrumbList", "itemListElement": [
                 {"@type": "ListItem", "position": 1, "name": "Three Moves Ago", "item": BASE + "/"},
                 {"@type": "ListItem", "position": 2, "name": crumbs[0], "item": BASE + crumbs[1]},
                 {"@type": "ListItem", "position": 3, "name": h1, "item": BASE + path}]}]
    faq_html = ''
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub('<[^>]+>', '', a)}} for q, a in faq]})
        faq_html = f'<h2 id="faq">{"Întrebări frecvente" if lang == "ro" else "Frequently asked questions"}</h2>\n' + ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in faq)
    ld = {"@context": "https://schema.org", "@graph": graph}
    return page(title, desc, path, f'<h1>{h1}</h1>\n{body}\n{faq_html}\n{cta or CTA}', 'article', ld, lang, alternates)

LEARN = {
'retrograde-analysis': article(
 'Retrograde Analysis in Chess: A Complete Guide with Examples',
 'Retrograde analysis in chess',
 'Retrograde analysis is reasoning backwards from a chess position to work out what happened before. Learn the clues, the main problem types, worked examples and the conventions, then try a daily retro puzzle.',
 '/learn/retrograde-analysis', f'''
<p class="lead">Retrograde analysis is the art of reasoning backwards in chess. Instead of asking “what is the best move?”, you look at a position and work out what must already have happened: which moves were played, what was captured, and in what order.</p>
<nav class="card" aria-label="Contents"><b>On this page</b><ol style="margin:6px 0 0">
<li><a href="#what">What is retrograde analysis?</a></li>
<li><a href="#clues">The clues retro solvers use</a></li>
<li><a href="#example">Worked example: the queen that came home</a></li>
<li><a href="#tempo">Tempo: the moves you cannot see</a></li>
<li><a href="#types">Types of retro problems</a></li>
<li><a href="#conventions">Conventions: castling and en passant</a></li>
<li><a href="#computers">Retrograde analysis in computer chess</a></li>
<li><a href="#method">A step-by-step method</a></li>
<li><a href="#faq">FAQ</a></li>
</ol></nav>

<h2 id="what">What is retrograde analysis?</h2>
<p>Every chess position is the end of a story. Pieces cannot jump over each other (except the knight), pawns never move backwards, and a captured piece never returns. Because the rules are so strict, a position often holds enough evidence to rebuild part of the game that produced it. Reconstructing that history is called <b>retrograde analysis</b>, usually shortened to <b>retro analysis</b> or just <b>retro</b>.</p>
<p>In over-the-board play it hardly matters how a position arose. In chess problems it is the whole point. Retro problems are a long-standing branch of chess composition, and they reached a wide audience through the logician Raymond Smullyan, whose books <i>The Chess Mysteries of Sherlock Holmes</i> and <i>The Chess Mysteries of the Arabian Knights</i> turn retro puzzles into detective stories.</p>

<h2 id="clues">The clues retro solvers use</h2>
<ul>
<li><b>Material.</b> Count the pieces. Every missing piece was captured, and every capture was made by a piece of the other colour. Sixteen pieces per side at the start means the count is always exact.</li>
<li><b>Pawn files.</b> A pawn can only change file by capturing. A pawn on a different file from where it started, or two pawns on the same file, proves that captures happened, and tells you how many.</li>
<li><b>Bishops and square colours.</b> A bishop stays on its colour forever. A light-squared bishop on a dark square must be a promoted piece.</li>
<li><b>Pieces that cannot have left.</b> A bishop behind its own unmoved pawns has never moved. A rook boxed in by its own king and pawns has not moved either.</li>
<li><b>Kings.</b> A king away from its home square walked there one square per move, and never through a square that was attacked at the time.</li>
<li><b>Checks.</b> Only one side can be in check, and the check must come from the last move. A double check can only arise in certain ways, which often pins down the last move exactly.</li>
<li><b>Tempo.</b> If a side needed fewer moves than it actually played, the spare moves went somewhere. A piece that went out and came back is the classic answer.</li>
</ul>

<h2 id="example">Worked example: the queen that came home</h2>
<p>From the starting position, White and Black have each played exactly three moves, and this is the result:</p>
{boards((START, 'Start'), (EX1, 'After three moves each'))}
<p><b>Read the evidence.</b> White is missing the e-pawn and has a knight on c3. Black is missing the d-pawn, and at first sight nothing else of Black’s has moved.</p>
<p><b>Count the captures.</b> Both sides lost a pawn, so there were two captures: one by White, one by Black.</p>
<p><b>Find the capturers.</b> The only white piece that can capture a pawn without leaving a trace is the e-pawn itself: it took on d5. Then a black piece captured that pawn on d5, and it must be a piece that is now back home, because Black has nothing standing on d5. The queen is the only black piece that can reach d5 and return to d8 in time.</p>
<p class="moves">1. e4 d5 2. exd5 Qxd5 3. Nc3 Qd8</p>
<p>The queen on d8 looks as if it never moved, but it went out, captured and returned. That is the essential retro trick: the position hides moves that left no visible mark.</p>

<h2 id="tempo">Tempo: the moves you cannot see</h2>
<p>Here is a puzzle with no diagram, because the answer is the starting position itself. After two moves by each side the board looks exactly like the start. What was played? Both sides had to spend two moves without changing anything, so each side moved a knight out and back:</p>
<p class="moves">1. Nf3 Nf6 2. Ng1 Ng8</p>
<p>(Other knight moves work too, which is why a good retro problem must be built so that only one sequence fits.) Tempo reasoning, asking “where did the spare moves go?”, solves a large share of retro problems.</p>

<h2 id="types">Types of retro problems</h2>
<ul>
<li><b>Proof games.</b> Find a game that reaches a given position in a given number of moves. When the number is the smallest possible, it is a <i>shortest proof game</i>. Read more in <a href="/learn/proof-games">What is a proof game?</a></li>
<li><b>Last-move problems.</b> “What was the last move?” The position allows exactly one legal last move, and you have to prove which.</li>
<li><b>Legality problems.</b> Is this position reachable at all? Or which piece, added to the board, would make it legal?</li>
<li><b>Castling and en passant problems.</b> Can White still castle? Is an en passant capture possible right now? Both depend on history, not on the position alone.</li>
<li><b>Retractors.</b> You take moves back instead of playing them forward, then usually deliver mate.</li>
</ul>

<h2 id="conventions">Conventions: castling and en passant</h2>
<p>Because the right to castle and the right to capture en passant depend on the past, retro composers follow agreed conventions. Castling is assumed to be allowed unless it can be proved that the king or rook has moved. An en passant capture is allowed only if it can be proved that the last move was the two-square pawn advance. Many of the most elegant retro problems turn on exactly these two rules.</p>

<h2 id="computers">Retrograde analysis in computer chess</h2>
<p>The same name is used for a different technique in chess programming. Endgame tablebases, which know the perfect result of every position with a few pieces, are built by retrograde analysis: the program starts from every checkmate and works backwards, move by move, to label every position as a win, draw or loss. The idea is the same, reasoning from the end back to the beginning, but here a computer does it for every position at once.</p>

<h2 id="method">A step-by-step method</h2>
<ol>
<li>Compare the position with the starting position and list everything that changed.</li>
<li>Count the missing pieces on both sides: that is the number of captures.</li>
<li>For each capture, find which enemy piece could have made it, and when.</li>
<li>Count how many moves the visible changes need, and compare with the moves available. Spare moves are hidden somewhere.</li>
<li>Use checks and pins to fix the order.</li>
</ol>
<p>A longer version with common traps is in <a href="/learn/how-to-solve">How to solve retro chess puzzles</a>.</p>

<h2>Practise every day</h2>
<p><a href="/">Three Moves Ago</a> is a free daily retrograde analysis puzzle: you get a target position and have to find the three moves each side played to reach it. Browse <a href="/cases">all past cases</a>, or start with today’s.</p>
''', faq=[
 ('What is retrograde analysis in chess?', 'Retrograde analysis (retro analysis) is reasoning backwards from a chess position to work out what happened earlier in the game: which moves were played, which pieces were captured, and in what order.'),
 ('Who made retrograde analysis popular?', 'Retro problems are an old branch of chess composition. The logician Raymond Smullyan brought them to a wide audience with <i>The Chess Mysteries of Sherlock Holmes</i> and <i>The Chess Mysteries of the Arabian Knights</i>.'),
 ('What is the difference between retrograde analysis and a proof game?', 'Retrograde analysis is the general method of reasoning backwards. A proof game is one type of retro problem, where you must find the exact game that reaches a given position in a given number of moves.'),
 ('Is retrograde analysis used by chess engines?', 'Yes, in a different sense: endgame tablebases are built by retrograde analysis, starting from checkmates and working backwards to label every position as a win, draw or loss.'),
 ('Where can I practise retrograde analysis?', 'Three Moves Ago publishes a free retro puzzle every day: find the three moves by White and the three by Black that lead to the target position.'),
], alternates=[('en', '/learn/retrograde-analysis'), ('ro', '/ro/analiza-retrograda'), ('x-default', '/learn/retrograde-analysis')]),
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


RO = article(
 'Analiza retrogradă în șah: ghid complet cu exemple – Three Moves Ago',
 'Analiza retrogradă în șah',
 'Analiza retrogradă înseamnă să raționezi înapoi de la o poziție de șah ca să afli ce s-a întâmplat înainte. Indiciile, tipurile de probleme, exemple rezolvate și un puzzle retro zilnic gratuit.',
 '/ro/analiza-retrograda', f"""
<p class="lead">De obicei, la șah te gândești înainte: care e cea mai bună mutare? Analiza retrogradă merge invers. Te uiți la o poziție și afli ce trebuie să se fi întâmplat deja.</p>
<h2>Ce este analiza retrogradă?</h2>
<p>Fiecare poziție de șah e finalul unei povești. Piesele nu sar unele peste altele (în afară de cal), pionii nu se mută înapoi, iar o piesă capturată nu se mai întoarce. Pentru că regulile sunt atât de stricte, poziția conține adesea destule dovezi ca să reconstruiești o parte din partida care a dus la ea. Asta se numește <b>analiză retrogradă</b> (în engleză <i>retrograde analysis</i> sau, pe scurt, <i>retro</i>).</p>
<p>În partidele obișnuite nu contează cum s-a ajuns la o poziție. În problemele de șah, exact asta e ideea. Problemele retro sunt o ramură veche a compoziției șahiste, făcute cunoscute publicului larg de logicianul Raymond Smullyan, în cartea <i>The Chess Mysteries of Sherlock Holmes</i>.</p>
<h2>Indiciile pe care le folosești</h2>
<ul>
<li><b>Materialul.</b> Numără piesele. Fiecare piesă lipsă a fost capturată, de o piesă de cealaltă culoare.</li>
<li><b>Coloanele pionilor.</b> Un pion schimbă coloana doar când capturează. Un pion pe altă coloană sau doi pioni pe aceeași coloană dovedesc o captură.</li>
<li><b>Nebunii și culoarea câmpurilor.</b> Un nebun rămâne mereu pe aceeași culoare.</li>
<li><b>Regii.</b> Un rege plecat de acasă a mers câte un câmp pe mutare, doar prin câmpuri neatacate.</li>
<li><b>Șahurile.</b> Doar o parte poate fi în șah, iar șahul vine de la ultima mutare. Asta fixează adesea ordinea.</li>
<li><b>Tempo-urile.</b> Dacă o parte avea nevoie de mai puține mutări decât a făcut, mutările în plus s-au dus undeva: o piesă a plecat și s-a întors.</li>
</ul>
<h2>Exemplu rezolvat: dama care s-a întors acasă</h2>
<p>De la poziția inițială, albul și negrul au făcut câte trei mutări și s-a ajuns aici:</p>
{boards((START, 'Start'), (EX1, 'După câte trei mutări'))}
<p>Albului îi lipsește pionul e, iar calul e pe c3. Negrului îi lipsește pionul d, și pare că nimic altceva nu s-a mutat. Au fost deci două capturi. Pionul alb e a luat pe d5, apoi o piesă neagră a luat pionul alb pe d5 și s-a întors acasă. Singura care poate face asta la timp e dama:</p>
<p class="moves">1. e4 d5 2. exd5 Dxd5 3. Cc3 Dd8</p>
<p>Dama de pe d8 pare că nu s-a mișcat, dar a plecat, a capturat și s-a întors. Acesta e trucul de bază al problemelor retro: poziția ascunde mutări care nu lasă urme.</p>
<h2>Tipuri de probleme retro</h2>
<ul>
<li><b>Partide-dovadă (proof games):</b> găsește partida care ajunge la o poziție dată într-un număr exact de mutări.</li>
<li><b>Ultima mutare:</b> ce mutare s-a jucat ultima? Poziția permite una singură.</li>
<li><b>Legalitate:</b> se poate ajunge la această poziție?</li>
<li><b>Rocadă și en passant:</b> mai poate albul face rocadă? E posibilă o captură en passant acum?</li>
</ul>
<p>În programarea șahului, același nume denumește metoda prin care se construiesc bazele de date de finaluri (tablebases): calculatorul pornește de la toate pozițiile de mat și lucrează înapoi.</p>
<h2>Exersează zilnic</h2>
<p><a href="/">Three Moves Ago</a> îți dă în fiecare zi un puzzle de analiză retrogradă, gratuit: primești o poziție și trebuie să găsești cele 3 mutări ale albului și cele 3 ale negrului care au dus la ea. Jocul e în engleză și folosește notația engleză: Q = dama, R = turnul, B = nebunul, N = calul, K = regele.</p>
""", faq=[
 ('Ce este analiza retrogradă în șah?', 'Analiza retrogradă înseamnă să raționezi înapoi de la o poziție de șah ca să afli ce s-a întâmplat mai devreme în partidă: ce mutări s-au jucat, ce piese au fost capturate și în ce ordine.'),
 ('Ce este o partidă-dovadă (proof game)?', 'O problemă retro în care trebuie să găsești partida exactă care ajunge la o poziție dată într-un număr fix de mutări.'),
 ('Unde pot exersa analiza retrogradă?', 'Pe Three Moves Ago apare în fiecare zi un puzzle retro gratuit: găsești cele 3 mutări ale fiecărei părți care au dus la poziția dată.'),
], lang='ro', alternates=[('en', '/learn/retrograde-analysis'), ('ro', '/ro/analiza-retrograda'), ('x-default', '/learn/retrograde-analysis')],
 crumbs=('Învață', '/learn/'), cta='<div class="cta"><a class="play" href="/">Joacă puzzle-ul de azi</a></div>')

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
ro = ROOT / 'public/ro'; ro.mkdir(exist_ok=True); (ro / 'analiza-retrograda.html').write_text(RO)
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
