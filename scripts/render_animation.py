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
FONT = find_font(args.font, ['/System/Library/Fonts/SFNS.ttf','/System/Library/Fonts/Supplemental/Arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
PIECE = find_font(args.piece_font, ['/System/Library/Fonts/Apple Symbols.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
fonts = {n:ImageFont.truetype(FONT,n) for n in [20,36,44]}
# Match the game's macOS system font and medium heading weight.
for size,font in fonts.items():
    try:
        axes=font.get_variation_axes()
        font.set_variation_by_axes([500 if axis['name']==b'Weight' and size==44 else min(max(size,axis['minimum']),axis['maximum']) if axis['name']==b'Optical Size' else axis['default'] for axis in axes])
    except OSError:
        pass  # Non-variable fonts supplied through --font.
knight_font = ImageFont.truetype(PIECE,88)
W,H=1000,541
BOARD_X,BOARD_Y,CELL,GAP=46,16,79,7
STEP=CELL+GAP
GREEN=(98,181,130)
def rgb(hex): return tuple(bytes.fromhex(hex.lstrip('#')))
def mix(a,b,t): return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def legal(a,b): return abs(a%6-b%6)*abs(a//6-b//6)==2

def frame(theme,index,next_index=None,t=0):
    bg,fg,muted,tile,dot = themes[theme]
    image=Image.new('RGB',(W,H),bg);draw=ImageDraw.Draw(image)
    current=TOUR[index]
    visited=set(TOUR[:index+1])
    for square in range(36):
        fill=tile
        if square in visited:
            age=index-TOUR.index(square)
            if age < 10:fill=mix(tile,GREEN,.12+(9-age)/9*.55)
        if square==current:fill=GREEN
        x,y=BOARD_X+square%6*STEP,BOARD_Y+square//6*STEP
        draw.rounded_rectangle((x,y,x+CELL-1,y+CELL-1),radius=11,fill=fill)
        if square not in visited and legal(current,square):
            cx,cy=x+CELL/2,y+CELL/2
            draw.ellipse((cx-5,cy-5,cx+5,cy+5),fill=dot)
    next_square=TOUR[next_index] if next_index is not None else current
    ease=t*t*(3-2*t)
    x=BOARD_X+((current%6)*(1-ease)+(next_square%6)*ease)*STEP+CELL/2
    y=BOARD_Y+((current//6)*(1-ease)+(next_square//6)*ease)*STEP+CELL/2-9*math.sin(t*math.pi)
    # Pale piece stays legible while it crosses the darker cells.
    draw.text((x,y),'♞',font=knight_font,fill=fg,anchor='mm',stroke_width=2,stroke_fill=bg)
    tx=604
    for i,line in enumerate(['One knight.','Every square.','Exactly once.']):
        draw.text((tx,140+i*54),line,font=fonts[44],fill=fg)
    draw.text((tx,346),f'{index+1:02}',font=fonts[36],fill=fg)
    draw.text((tx+66,359),'/ 36 squares',font=fonts[20],fill=muted)
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
    piece=Image.new('RGBA',(45*scale,45*scale),(0,0,0,0))
    ImageDraw.Draw(piece).text(
        (45*scale/2,45*scale/2),'♞',
        font=ImageFont.truetype(PIECE,50*scale),fill=themes[theme][1],
        anchor='mm',stroke_width=scale,stroke_fill=themes[theme][0])
    piece.save(pieces/f'knight-{theme}.png',optimize=True)
    # A shared palette prevents the static text from flickering between frames.
    sample=Image.new('RGB',(W,H*4))
    for i,k in enumerate([0,7,18,35]):sample.paste(frame(theme,k),(0,H*i))
    palette=sample.quantize(colors=96,method=Image.Quantize.MEDIANCUT)
    frames=[];durations=[]
    for index in range(36):
        still=frame(theme,index)
        frames.append(still.quantize(palette=palette,dither=Image.Dither.NONE));durations.append(400 if index!=35 else 1200)
        # Reset directly to move 1 after the completed board.
        if index == 35: continue
        for step in range(1,7):
            frames.append(frame(theme,index,(index+1)%36,step/7).quantize(palette=palette,dither=Image.Dither.NONE));durations.append(50)
    target=assets/f'knights-tour-{theme}.gif'
    frames[0].save(target,save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True,disposal=1)
    frame(theme,0).save(assets/f'knights-tour-{theme}.png',optimize=True)
    print(f'{target.name}: {target.stat().st_size:,} bytes, {len(frames)} frames',flush=True)
