# Maintaining the knight’s tour

This repository powers the profile at https://github.com/KingFeddy and the game at https://kingfeddy.github.io/KingFeddy/.

- `README.md` is the profile. Its images and play link point to the game.
- `assets/` contains the active light/dark SVG animations, plus older GIF and still-image exports.
- `docs/` contains the standalone game, published with GitHub Pages from `main` → `/docs`.
- `docs/tour.mjs` contains the 6×6 board rules and verified closed tour.
- `scripts/render_profile_svg.py` generates the active README animation with native SVG animation (no JavaScript).
- `scripts/render_animation.py` maintains the older GIF/still exports and shared knight PNGs using Pillow.

The board depicts a puzzle, not contribution history. The game requires no account, external service, build process, or data collection.

## Check the rules

Use Node.js 20 or newer:

```sh
node --test tests/tour.test.mjs
```

## Regenerate the images

Use Python 3 with Pillow installed:

```sh
python3 scripts/render_animation.py
```

The active profile uses `python3 scripts/render_profile_svg.py`. It reuses the game’s knight PNGs and renders vector tiles and system-font text. Each square lights on its visit, then drops in discrete brightness steps at each new move. Brightness stays constant between moves, including the longer pause at move 36. During the final hop back to the start, all remaining trail fades away together. Every lap, including the first load, starts clean with only the knight’s current square highlighted. The knight follows the closed tour back to the top-left square, with the counter returning to 01 on arrival. Normal moves take 700 ms; move 36 holds for 1.2 seconds before the final hop. The game itself is independent and retains permanent visited squares.

After committing regenerated SVGs, pin the image URLs in `README.md` to that commit SHA to avoid stale cached artwork. The Pillow script above remains available for older GIF and PNG exports; the active SVG is maintained separately.

## Preview the game

From the repository root:

```sh
python3 -m http.server 8000 --directory docs
```

Open http://localhost:8000. JavaScript modules need an HTTP server rather than opening the file directly.
