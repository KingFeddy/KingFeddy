"""Render the README animation. Requires Python 3 and Pillow; no network calls."""
from pathlib import Path
import argparse, json, math, re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TOUR = json.loads(re.search(r'Object.freeze\((\[[^;]+\])\)', (ROOT/'docs/tour.mjs').read_text()).group(1))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--font', help='Path to a sans-serif TrueType font')
parser.add_argument('--piece-font', help='Path to a font with the black knight chess glyph')
args = parser.parse_args()
def find_font(explicit, candidates):
    if explicit: return explicit
    for path in candidates:
        if Path(path).is_file(): return path
    raise SystemExit('Provide --font and --piece-font paths available on this machine.')
FONT = find_font(args.font, ['/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
PIECE = find_font(args.piece_font, ['/System/Library/Fonts/Apple Symbols.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
fonts = {n:ImageFont.truetype(FONT,n) for n in [13,14,16,19,28,36]}
knight_font = ImageFont.truetype(PIECE,50)
W,H=720,390
BOARD_X,BOARD_Y,CELL,GAP=25,48,45,5
STEP=CELL+GAP
GREEN=(98,181,130)
def rgb(hex): return tuple(bytes.fromhex(hex.lstrip('#')))
def mix(a,b,t): return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def legal(a,b): return abs(a%6-b%6)*abs(a//6-b//6)==2

def frame(theme,index,next_index=None,t=0):
    bg,fg,muted,tile,dot = themes[theme]
    image=Image.new('RGB',(W,H),bg);draw=ImageDraw.Draw(image)
    current=TOUR[index]
    trail=[TOUR[(index-9+i)%36] for i in range(10)]
    visited=set(TOUR[:index+1])
    draw.text((BOARD_X,12),'KNIGHT’S TOUR',fill=muted,font=fonts[13])
    for square in range(36):
        fill=tile
        if square in trail:fill=mix(tile,GREEN,.12+trail.index(square)/9*.55)
        if square==current:fill=GREEN
        x,y=BOARD_X+square%6*STEP,BOARD_Y+square//6*STEP
        draw.rounded_rectangle((x,y,x+CELL-1,y+CELL-1),radius=6,fill=fill)
        if square not in visited and legal(current,square):
            cx,cy=x+CELL/2,y+CELL/2
            draw.ellipse((cx-3,cy-3,cx+3,cy+3),fill=dot)
    next_square=TOUR[next_index] if next_index is not None else current
    ease=t*t*(3-2*t)
    x=BOARD_X+((current%6)*(1-ease)+(next_square%6)*ease)*STEP+CELL/2
    y=BOARD_Y+((current//6)*(1-ease)+(next_square//6)*ease)*STEP+CELL/2-5*math.sin(t*math.pi)
    # Pale piece stays legible while it crosses the darker cells.
    draw.text((x,y),'♞',font=knight_font,fill=fg,anchor='mm',stroke_width=1,stroke_fill=bg)
    tx=382
    draw.text((tx,64),'A SMALL CHESS DETOUR',font=fonts[13],fill=muted)
    for i,line in enumerate(['One knight.','Every square.','Exactly once.']):
        draw.text((tx,100+i*41),line,font=fonts[36],fill=fg)
    draw.text((tx,242),f'{index+1:02}',font=fonts[28],fill=fg)
    draw.text((tx+46,254),'/ 36 squares',font=fonts[14],fill=muted)
    draw.ellipse((tx,296,tx+6,302),fill=dot)
    draw.text((tx+16,291),'Available move',font=fonts[14],fill=muted)
    draw.line((25,362,695,362),fill=mix(bg,muted,.25))
    draw.text((25,372),'A little strategy between commits.',font=fonts[13],fill=muted)
    draw.text((625,372),'KingFeddy',font=fonts[13],fill=muted)
    return image

themes={
 'dark':tuple(map(rgb,['#0d1117','#e6edf3','#98a5b3','#19241f','#9addae'])),
 'light':tuple(map(rgb,['#ffffff','#1f2328','#59636e','#e8eee9','#286c43']))
}
assets=ROOT/'assets';assets.mkdir(exist_ok=True)
pieces=ROOT/'docs/assets';pieces.mkdir(exist_ok=True)
for theme in themes:
    # Use the animation's exact glyph, placement, and colors in the browser too.
    # A 4x transparent asset avoids OS-dependent font substitution and stays crisp.
    scale=4
    piece=Image.new('RGBA',(CELL*scale,CELL*scale),(0,0,0,0))
    ImageDraw.Draw(piece).text(
        (CELL*scale/2,CELL*scale/2),'♞',
        font=ImageFont.truetype(PIECE,50*scale),fill=themes[theme][1],
        anchor='mm',stroke_width=scale,stroke_fill=themes[theme][0])
    piece.save(pieces/f'knight-{theme}.png',optimize=True)
    # A shared palette prevents the static text from flickering between frames.
    sample=Image.new('RGB',(W,H*4))
    for i,k in enumerate([0,7,18,35]):sample.paste(frame(theme,k),(0,H*i))
    palette=sample.quantize(colors=96,method=Image.Quantize.MEDIANCUT)
    frames=[];durations=[]
    for offset in range(36):
        index=(7+offset)%36
        still=frame(theme,index)
        frames.append(still.quantize(palette=palette,dither=Image.Dither.NONE));durations.append(420 if index!=35 else 1400)
        for step in range(1,7):
            frames.append(frame(theme,index,(index+1)%36,step/7).quantize(palette=palette,dither=Image.Dither.NONE));durations.append(60)
    target=assets/f'knights-tour-{theme}.gif'
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True,disposal=1)
    frame(theme,7).save(assets/f'knights-tour-{theme}.png',optimize=True)
    print(f'{target.name}: {target.stat().st_size:,} bytes, {len(frames)} frames',flush=True)
