"""Generate a continuous README tour with a clean first pass (no JavaScript)."""
from pathlib import Path
import base64
import json
import math
import re
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
TOUR = json.loads(re.search(r'Object.freeze\((\[[^;]+\])\)', (ROOT / 'docs/tour.mjs').read_text()).group(1))
W, H = 1000, 541
X, Y, CELL, STEP = 46, 16, 79, 86
MOVE, HOLD, LAST_HOLD = .7, .4, 1.2
PERIOD = 35 * MOVE + LAST_HOLD + (MOVE - HOLD)
THEMES = {
    'dark': ('#0d1117', '#e6edf3', '#98a5b3', '#19241f', '#9addae'),
    'light': ('#ffffff', '#1f2328', '#59636e', '#e8eee9', '#286c43'),
}

def num(value):
    return f'{value:.7f}'.rstrip('0').rstrip('.') or '0'

def xy(square):
    return X + square % 6 * STEP, Y + square // 6 * STEP

def legal(a, b):
    return abs(a % 6 - b % 6) * abs(a // 6 - b // 6) == 2

def discrete(values):
    # Repeated 26-second timeline for counters and available-move dots.
    times = [i * MOVE / PERIOD for i in range(36)] + [1]
    return (f'<animate attributeName="opacity" dur="{num(PERIOD)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{";".join(map(num, times))}" '
            f'values="{";".join(map(str, values + [values[0]]))}"/>')

def trail_steps(visit):
    # Age the glow by completed moves, including the longer hold at move 36.
    arrivals = [((visit + age) // 36) * PERIOD + ((visit + age) % 36) * MOVE
                - visit * MOVE for age in range(11)]
    levels = [1] + [.12 + (9 - age) / 9 * .55 for age in range(1, 10)] + [0]
    return arrivals + [PERIOD], levels + [0]

def render(theme):
    bg, fg, muted, tile, dot = THEMES[theme]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
           '<title id="title">One knight. Every square. Exactly once.</title>',
           '<desc id="desc">A knight visits all 36 squares, then returns to the top left. Its fading trail continues across each loop.</desc>',
           f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    for square in range(36):
        x, y = xy(square)
        visit = TOUR.index(square)
        fade_times, fade_levels = trail_steps(visit)
        # Delayed start means unvisited squares have no trail on first load.
        # Each square advances one fade step per arrival, across loop boundaries.
        out += [f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="11" fill="{tile}"/>',
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="11" fill="#62b582" opacity="0">',
                f'<animate attributeName="opacity" begin="{num(visit * MOVE)}s" dur="{num(PERIOD)}s" repeatCount="indefinite" '
                f'calcMode="discrete" keyTimes="{";".join(num(t / PERIOD) for t in fade_times)}" '
                f'values="{";".join(map(num, fade_levels))}"/>', '</rect>']
        values = [int(visit > i and legal(TOUR[i], square)) for i in range(36)]
        if any(values):
            out += [f'<circle cx="{x + CELL / 2}" cy="{y + CELL / 2}" r="5" fill="{dot}" opacity="{values[0]}">', discrete(values), '</circle>']
    # Sample the same eased hopping motion as the GIF, including the final
    # legal knight move back to square zero. End and start positions coincide.
    times, positions = [0], [xy(TOUR[0])]
    for index, square in enumerate(TOUR):
        start = index * MOVE
        hold = LAST_HOLD if index == 35 else HOLD
        ax, ay = xy(square)
        bx, by = xy(TOUR[(index + 1) % 36])
        times.append((start + hold) / PERIOD)
        positions.append((ax, ay))
        for step in range(1, 13):
            t = step / 12
            ease = t * t * (3 - 2 * t)
            times.append((start + hold + .3 * t) / PERIOD)
            positions.append((ax + (bx - ax) * ease, ay + (by - ay) * ease - 9 * math.sin(t * math.pi)))
    png = base64.b64encode((ROOT / f'docs/assets/knight-{theme}.png').read_bytes()).decode()
    out += [f'<g transform="translate({X} {Y})">',
            f'<animateTransform attributeName="transform" type="translate" dur="{num(PERIOD)}s" repeatCount="indefinite" calcMode="linear" '
            f'keyTimes="{";".join(map(num, times))}" values="{";".join(f"{num(x)} {num(y)}" for x, y in positions)}"/>',
            f'<image width="{CELL}" height="{CELL}" xlink:href="data:image/png;base64,{png}"/>', '</g>',
            f'<g fill="{fg}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">']
    for index, line in enumerate(['One knight.', 'Every square.', 'Exactly once.']):
        out.append(f'<text x="604" y="{182 + index * 54}" font-size="44" font-weight="500" letter-spacing="-1">{escape(line)}</text>')
    for index in range(36):
        values = [int(i == index) for i in range(36)]
        out += [f'<text x="604" y="374" font-size="36" opacity="{values[0]}">{index + 1:02}', discrete(values), '</text>']
    out += [f'<text x="670" y="378" font-size="20" fill="{muted}">/ 36 squares</text>', '</g>', '</svg>']
    return '\n'.join(out)

if __name__ == '__main__':
    for theme in THEMES:
        target = ROOT / f'assets/knights-tour-{theme}.svg'
        target.write_text(render(theme))
        print(f'{target.name}: {target.stat().st_size:,} bytes')
