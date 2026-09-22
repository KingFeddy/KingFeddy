import {SIZE, TOTAL, TOUR, legalMoves, move, status} from './tour.mjs';
const root = document.getElementById('knights-tour-game');
const q = selector => root.querySelector(selector);
const motion = matchMedia('(prefers-reduced-motion: reduce)');
let mode = 'play', running = !motion.matches, index = 0, path = [0], previous = -1, lastTime = performance.now();
const cells = Array.from({length: TOTAL}, (_, i) => {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'kt-square';
  button.addEventListener('click', () => {
    if (mode !== 'play') return;
    const next = move(path, i);
    if (next === path) return;
    const hadFocus = button.matches(':focus');
    path = next;
    render();
    // The selected square becomes disabled; move keyboard focus to a valid next move.
    if (hadFocus) (cells[legalMoves(path)[0]] ?? q('.kt-try')).focus();
  });
  q('.kt-grid').append(button);
  return button;
});
function positionKnight(square) {
  const step = (q('.kt-board').clientWidth + 5) / SIZE;
  q('.kt-knight').style.transform = `translate(${square % SIZE * step}px,${Math.floor(square / SIZE) * step}px)`;
}
function render() {
  const history = mode === 'play' ? path : TOUR.slice(0, index + 1);
  const current = history.at(-1);
  const legal = legalMoves(history);
  root.dataset.paused = String(!running);
  cells.forEach((button, i) => {
    button.className = 'kt-square' + (i === current ? ' current' : '') + (legal.includes(i) ? ' legal' : '');
    button.style.background = history.includes(i) ? 'color-mix(in srgb,var(--kt-green) 50%,var(--kt-tile))' : '';
    button.disabled = mode !== 'play' || !legal.includes(i);
    const coordinate = `${String.fromCharCode(65 + i % SIZE)}${SIZE - Math.floor(i / SIZE)}`;
    button.setAttribute('aria-label', coordinate + (i === current ? ', knight' : history.includes(i) ? ', visited' : legal.includes(i) ? ', available move' : ''));
  });
  positionKnight(current);
  if (previous !== current && !motion.matches) {
    q('.kt-knight').classList.remove('hopping');
    void q('.kt-knight').offsetWidth;
    q('.kt-knight').classList.add('hopping');
  }
  previous = current;
  q('.kt-count strong').textContent = String(history.length).padStart(2, '0');
  q('.kt-count').setAttribute('aria-label', `${history.length} of ${TOTAL} squares visited`);
  q('.kt-pause').hidden = mode === 'play';
  q('.kt-pause').textContent = running ? 'Pause animation' : 'Play animation';
  q('.kt-try').textContent = mode === 'play' ? 'Start again ↻' : 'Play Horseplay ↗';
  q('.kt-back').hidden = mode === 'watch';
  q('.kt-kicker').textContent = mode === 'play' ? 'YOUR MOVE' : 'A COMPLETE TOUR';
  const result = status(history);
  const heading = mode === 'play' && result === 'blocked' ? "You're stuck.<br>GGs"
    : mode === 'play' && result === 'complete' ? 'Good Job!<br>Take this 🏆'
    : "Make 'em<br>dance<span>!</span>";
  if (q('h2').innerHTML !== heading) q('h2').innerHTML = heading;
}
q('.kt-try').addEventListener('click', () => { mode = 'play'; path = [0]; render(); });
q('.kt-back').addEventListener('click', () => {
  mode = 'watch';
  index = 0;
  running = !motion.matches;
  lastTime = performance.now();
  render();
});
q('.kt-pause').addEventListener('click', () => { running = !running; lastTime = performance.now(); render(); });
motion.addEventListener('change', () => { if (motion.matches) running = false; render(); });
new ResizeObserver(() => positionKnight(mode === 'play' ? path.at(-1) : TOUR[index])).observe(q('.kt-board'));
render();
function frame(now) {
  if (mode === 'watch' && running && !document.hidden && now - lastTime > (index === TOTAL - 1 ? 1200 : 700)) {
    lastTime = now;
    index = (index + 1) % TOTAL;
    render();
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
