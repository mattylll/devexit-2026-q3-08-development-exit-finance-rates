import {calculate} from './model.mjs';
const $=id=>document.getElementById(id);
const money=new Intl.NumberFormat('en-GB',{style:'currency',currency:'GBP',maximumFractionDigits:0});
const fmt=n=>money.format(Math.abs(n));
let current=null;
const labels=['Gross facility','Less: retained interest','Less: arrangement fee','Less: other completion costs','Net day-one advance','Less: existing loan redemption','Balance after redemption'];
function update(){
  const inputs=[...document.querySelectorAll('input')];let valid=true;
  for(const input of inputs){const ok=input.validity.valid&&Number.isFinite(input.valueAsNumber);input.setAttribute('aria-invalid',String(!ok));valid=valid&&ok;}
  $('error').hidden=valid;$('results').hidden=!valid;current=null;if(!valid)return;
  const v=Object.fromEntries(inputs.map(x=>[x.id,x.valueAsNumber]));
  const a=calculate({...v,rate:v.rateA,months:v.monthsA}),b=calculate({...v,rate:v.rateB,months:v.monthsB});
  current={v,a,b};
  for(const [key,r] of [['A',a],['B',b]]){
    const short=r.balance < -0.005, balanced=Math.abs(r.balance)<0.005;
    $('card'+key).className='result '+(short?'shortfall':'surplus');
    $('status'+key).textContent=short?'Cash shortfall at completion':balanced?'Redemption covered exactly':'Available after redemption';
    $('balance'+key).textContent=fmt(r.balance);
    $('note'+key).textContent=short?'Additional cash or a revised structure would be needed in this model.':balanced?'No balance remains for any costs outside these assumptions.':'This is before any costs or funding needs not entered above.';
  }
  const rows=[[v.gross,v.gross],[a.interest,b.interest],[a.arrangement,b.arrangement],[v.costs,v.costs],[a.net,b.net],[v.redemption,v.redemption],[a.balance,b.balance]];
  $('bridge').replaceChildren(...rows.map((row,i)=>{const tr=document.createElement('tr');if(i===4||i===6)tr.className='total';const th=document.createElement('th');th.scope='row';th.textContent=labels[i];tr.append(th);for(const val of row){const td=document.createElement('td');td.textContent=money.format(val);tr.append(td);}return tr;}));
  $('required').textContent=['A','B'].map((k,i)=>{const r=i?b:a;return `Structure ${k}: gross needed to cover this redemption and these deductions = ${r.requiredGross===null?'no finite positive solution':money.format(r.requiredGross)}.`;}).join(' ')+' This is arithmetic only, not an available loan amount.';
}
$('inputs').addEventListener('input',update);$('inputs').addEventListener('submit',e=>e.preventDefault());
$('reset').addEventListener('click',()=>{$('inputs').reset();update();});
$('print').addEventListener('click',()=>window.print());
$('download').addEventListener('click',()=>{
  if(!current)return;const {v,a,b}=current;
  const rows=[['DevExit DX-02','Illustrative net advance comparison','2026-11-03'],['All amounts GBP; rates and fees in percent. Not a quote.'],['Input or output','Structure A','Structure B'],['Gross facility',v.gross,v.gross],['Existing redemption',v.redemption,v.redemption],['Monthly simple rate (%)',v.rateA,v.rateB],['Reserve months',v.monthsA,v.monthsB],['Arrangement fee (%)',v.fee,v.fee],['Other completion costs',v.costs,v.costs],['Retained interest',a.interest,b.interest],['Arrangement fee amount',a.arrangement,b.arrangement],['Net day-one advance',a.net,b.net],['Balance after redemption',a.balance,b.balance],['Gross needed in model',a.requiredGross??'No finite positive solution',b.requiredGross??'No finite positive solution'],['Method','Simple interest on gross; deductions once; no compounding; no sales repayments.'],['Source',document.querySelector('link[rel=canonical]').href],['Original content and code: all rights reserved. No source dataset included.']];
  const csv=rows.map(row=>row.map(x=>'"'+(typeof x==='number'?x.toFixed(2):String(x)).replaceAll('"','""')+'"').join(',')).join('\r\n');
  const url=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv;charset=utf-8'}));const link=document.createElement('a');link.href=url;link.download='devexit-net-advance-comparison.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
update();
