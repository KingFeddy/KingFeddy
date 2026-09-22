import test from 'node:test';
import assert from 'node:assert/strict';
import {SIZE,TOTAL,TOUR,isKnightMove,legalMoves,move,status} from '../docs/tour.mjs';
test('demo visits every square once and closes with a legal move',()=>{
  assert.equal(SIZE,6);assert.equal(TOTAL,36);assert.equal(TOUR.length,TOTAL);assert.equal(new Set(TOUR).size,TOTAL);
  TOUR.forEach((square,i)=>assert.ok(isKnightMove(square,TOUR[(i+1)%TOTAL])));
});
test('corners, center, invalid coordinates, and repeated squares',()=>{
  assert.deepEqual(legalMoves([0]),[8,13]);
  assert.equal(legalMoves([14]).length,8);
  for(const bad of [-1,36,1.2,NaN,'8'])assert.equal(isKnightMove(0,bad),false);
  const path=[0,8];assert.equal(move(path,0),path);assert.equal(move(path,9),path);assert.equal(move(path,36),path);
});
test('playable complete tour, blocked route, and immutable moves',()=>{
  let path=[0];
  for(const square of TOUR.slice(1)){const old=path;path=move(path,square);assert.notEqual(path,old);assert.equal(path.length,old.length+1)}
  assert.equal(status(path),'complete');assert.deepEqual(legalMoves(path),[]);
  let blocked=[0];while(legalMoves(blocked).length)blocked=move(blocked,legalMoves(blocked)[0]);
  assert.ok(blocked.length<TOTAL);assert.equal(status(blocked),'blocked');assert.equal(status([0]),'playing');
});
