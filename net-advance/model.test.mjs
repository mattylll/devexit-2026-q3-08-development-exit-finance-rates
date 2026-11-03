import {test} from 'node:test';
import assert from 'node:assert/strict';
import {calculate} from './model.mjs';
const base = {gross:3300000,redemption:3000000,fee:2,costs:20000};
test('lower rate can have a larger reserve and a day-one shortfall',()=>{
  const a=calculate({...base,rate:0.65,months:12}), b=calculate({...base,rate:0.85,months:6});
  assert.equal(a.interest,257400); assert.equal(a.net,2956600); assert.equal(a.balance,-43400);
  assert.equal(b.interest,168300); assert.equal(b.net,3045700); assert.equal(b.balance,45700);
});
test('required gross actually clears redemption under the same deductions',()=>{
  const p={...base,rate:0.65,months:12};const r=calculate(p);
  assert.ok(Math.abs(calculate({...p,gross:r.requiredGross}).balance)<0.000001);
});
test('with the same retention period a lower rate improves net proceeds',()=>{
  assert.ok(calculate({...base,rate:0.65,months:12}).net>calculate({...base,rate:0.85,months:12}).net);
});
test('zero interest, zero fees and exact redemption produce zero balance',()=>{
  assert.equal(calculate({gross:3000000,redemption:3000000,rate:0,months:0,fee:0,costs:0}).balance,0);
});
test('deductions consuming the facility do not imply a finite required loan',()=>{
  const r=calculate({...base,rate:5,months:24});assert.equal(r.requiredGross,null);assert.ok(r.net<0);
});
test('reject missing, non-finite, negative and fractional-month inputs',()=>{
  for(const bad of [{rate:NaN},{gross:Infinity},{months:1.5},{costs:-1},{gross:0}]) {
    assert.throws(()=>calculate({...base,rate:0.65,months:12,...bad}),RangeError);
  }
});
