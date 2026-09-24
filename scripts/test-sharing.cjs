const assert=require('node:assert/strict');
const X=require('../src/experience.js');
const M=require('../src/app.js');
const base='https://example.com/project/brand-kiva.html';
const brands=['kiva','camino','wyld','pax'];
assert.deepEqual(X.unique(['kiva','evil','kiva','camino','wyld','pax'],brands),['kiva','camino','wyld']);
assert.equal(X.shareURL(base,'atlas',['kiva','camino']),'https://example.com/project/index.html?shortlist=kiva%2Ccamino#discovery');
const aromaURL=new URL(X.shareURL(base,'terpenes',['Citrus','Pine']));assert.equal(aromaURL.searchParams.get('aromas'),'Citrus,Pine');
assert.equal(X.signature(['Pine','Fresh']).name,'Forest Dweller');assert.equal(X.signature([]).name,'Find your signature.');
for(const state of [{city:'san-jose',subtotal:60,tax:null,tip:0,fulfillment:'delivery'},{city:'campbell',subtotal:81.52,tax:18.29,tip:4.53,fulfillment:'pickup'}]){
 const u=new URL(X.shareURL(base,'delivery',state));const restored=X.plan(u.searchParams,['san-jose','campbell']);assert.deepEqual(restored,state);const before=M.budget({...state,fee:3.99,minimum:50});const after=M.budget({...restored,fee:3.99,minimum:50});assert.deepEqual(before,after);
}
const bad=X.plan(new URLSearchParams('city=evil&sub=-2&tax=oops&tip=Infinity&mode=other'),['san-jose']);assert.deepEqual(bad,{city:'san-jose',subtotal:60,tax:null,tip:0,fulfillment:'delivery'});
assert.equal(new URL(X.shareURL(base,'delivery',{city:'san-jose',subtotal:1,tax:null,tip:0,fulfillment:'delivery'})).searchParams.has('tax'),false);
console.log('PASS: share-link round trips, project subpaths, unknown IDs, duplicate limits, negative inputs, blank-tax semantics, scent signatures.');
