export const SIZE = 6;
export const TOTAL = SIZE * SIZE;
export const TOUR = Object.freeze([0,8,4,17,28,32,24,20,31,18,7,3,11,15,2,6,19,30,26,34,23,10,21,29,33,25,12,1,14,22,35,27,16,5,9,13]);
export function isKnightMove(from, to) {
  if (![from, to].every(n => Number.isInteger(n) && n >= 0 && n < TOTAL)) return false;
  return Math.abs(from % SIZE - to % SIZE) * Math.abs(Math.floor(from / SIZE) - Math.floor(to / SIZE)) === 2;
}
export function legalMoves(path) {
  const current = path.at(-1);
  return Array.from({length: TOTAL}, (_, i) => i).filter(i => !path.includes(i) && isKnightMove(current, i));
}
export function move(path, next) {
  return legalMoves(path).includes(next) ? [...path, next] : path;
}
export function status(path) {
  return path.length === TOTAL ? 'complete' : legalMoves(path).length ? 'playing' : 'blocked';
}
