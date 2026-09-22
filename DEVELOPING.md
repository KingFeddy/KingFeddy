# Maintaining the knight’s tour

This repository powers the profile at https://github.com/KingFeddy and the game at https://kingfeddy.github.io/KingFeddy/.

- `README.md` is the profile. Its images and play link point to the game.
- `assets/` contains light/dark GIF animations and optional still images. GitHub’s own animation preference controls profile playback.
- `docs/` contains the standalone game, published with GitHub Pages from `main` → `/docs`.
- `docs/tour.mjs` contains the 6×6 board rules and verified closed tour.
- `scripts/render_animation.py` regenerates the README images using Pillow.

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

The script detects common macOS/Linux fonts. Supply `--font` and `--piece-font` if needed; the piece font must contain the ♞ glyph. Images are generated locally. Commit the updated files in `assets/` to update the profile. The animation begins at move 1, uses the game’s 700 ms move interval, holds the last move for 1.2 seconds, and then loops. The profile animation uses a fading ten-square trail and keeps “Make 'em dance!” throughout; the playable game keeps permanent green squares and its win message. The optional still images also show move 1. Do not select them with a README reduced-motion media query: that can override an explicit GitHub autoplay preference. After committing regenerated assets, pin the image URLs in `README.md` to that commit SHA to avoid serving an older cached image. GitHub controls README playback; a restart on every browser refresh cannot be forced with README markup.

## Preview the game

From the repository root:

```sh
python3 -m http.server 8000 --directory docs
```

Open http://localhost:8000. JavaScript modules need an HTTP server rather than opening the file directly.
