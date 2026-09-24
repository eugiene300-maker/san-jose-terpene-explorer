'use strict';
const GuideMath = {
 budget({subtotal,tax,tip,fee,minimum,fulfillment}) {
  const values=[subtotal,tip,fee,...(tax===null?[]:[tax])];
  if(values.some(v=>typeof v!=='number'||!Number.isFinite(v)||v<0)||subtotal>10000||tip>1000||fee>1000||(tax!==null&&tax>10000))throw new Error('Enter non-negative amounts within the field limits.');
  const delivery=fulfillment==='delivery'?fee:0;
  return {total:Math.round((subtotal+(tax??0)+tip+delivery)*100)/100,delivery,preTax:tax===null,belowMinimum:fulfillment==='delivery'&&subtotal<minimum,gap:Math.max(0,minimum-subtotal)};
 },
 lab(values,unit){
  if(!['mgg','percent'].includes(unit))throw new Error('Choose a supported unit.');
  const entries=Object.entries(values).filter(([,v])=>v!==null);
  if(entries.some(([,v])=>typeof v!=='number'||!Number.isFinite(v)||v<0))throw new Error('Use non-negative numeric lab values.');
  const rows=entries.map(([id,v])=>({id,mgg:unit==='mgg'?v:v*10,percent:unit==='percent'?v:v/10}));
  const total=rows.reduce((s,r)=>s+r.percent,0);
  if(total>100+1e-9)throw new Error('The entered values exceed 100%. Check the report units and amounts.');
  return {rows,total,entered:rows.length};
 }
};
if(typeof module!=='undefined'&&module.exports)module.exports=GuideMath;
if(typeof document!=='undefined'){
const DATA=JSON.parse(document.getElementById('site-data').textContent),$=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(n);
const safe=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const cards=$$('[data-card]');let format='All';let selectedAromas=new Set();
function filterBrands(query,cat,origin){
 let count=0;cards.forEach(c=>{const show=c.dataset.search?.includes(query.toLowerCase().trim())&&(cat==='All'||c.dataset.category.split('|').includes(cat))&&(origin==='All'||c.dataset.origin===origin);c.hidden=!show;if(show)count++;});
 if($('#result-count'))$('#result-count').textContent=count+' brand'+(count===1?'':'s');if($('#empty'))$('#empty').hidden=count>0;return count;
}
function updateBrands(){return filterBrands($('#brand-search')?.value||'',format,$('#origin')?.value||'All');}
$('#brand-search')?.addEventListener('input',updateBrands);$('#origin')?.addEventListener('change',updateBrands);
$('#brand-search-form')?.addEventListener('submit',e=>{e.preventDefault();updateBrands();$('#directory').scrollIntoView({behavior:'smooth'});});
$$('[data-filter]').forEach(b=>b.addEventListener('click',()=>{format=b.dataset.filter;$$('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));updateBrands();}));
function updateAromas(){let count=0;cards.forEach(c=>{const show=!selectedAromas.size||c.dataset.aromas.split('|').some(v=>selectedAromas.has(v));c.hidden=!show;if(show)count++;});$$('[data-aroma]').forEach(b=>b.setAttribute('aria-pressed',String(selectedAromas.has(b.dataset.aroma))));if($('#result-count'))$('#result-count').textContent=count+' compound'+(count===1?'':'s');if($('#aroma-summary'))$('#aroma-summary').textContent=selectedAromas.size?'Matching any: '+[...selectedAromas].join(', '):'No aroma filters selected';if($('#empty'))$('#empty').hidden=count>0;document.dispatchEvent(new CustomEvent('aromas-changed'));return count;}
$$('[data-aroma]').forEach(b=>b.addEventListener('click',()=>{if(!selectedAromas.has(b.dataset.aroma)&&selectedAromas.size>=3){if($('#scent-limit'))$('#scent-limit').textContent='Choose up to three aromas. Deselect one to add another.';return;}selectedAromas.has(b.dataset.aroma)?selectedAromas.delete(b.dataset.aroma):selectedAromas.add(b.dataset.aroma);if($('#scent-limit'))$('#scent-limit').textContent='Aroma preferences only. Your signature does not predict cannabis effects.';updateAromas();}));
$('#aroma-reset')?.addEventListener('click',()=>{selectedAromas.clear();updateAromas();});
const selected=new Set();
function updateCompare(){const n=selected.size;$('#compare-bar').hidden=!n;$('#compare-count').textContent=n+' of 3 selected';$('#compare-open').disabled=n<2;}
$$('[data-compare]').forEach(c=>c.addEventListener('change',()=>{if(c.checked&&selected.size===3){c.checked=false;$('#selection-status').textContent='Compare up to three at a time. Remove one to add another.';return;}c.checked?selected.add(c.dataset.compare):selected.delete(c.dataset.compare);$('#selection-status').textContent='';updateCompare();}));
$('#compare-clear')?.addEventListener('click',()=>{selected.clear();$$('[data-compare]').forEach(c=>c.checked=false);updateCompare();});
$('#compare-open')?.addEventListener('click',()=>{const records=(DATA.kind==='atlas'?DATA.brands:DATA.terpenes).filter(x=>selected.has(x.id));let fields;
 if(DATA.kind==='atlas')fields=[['Geographic context',b=>b.region],['Formats',b=>b.formats.join(', ')],['What to ask',b=>b.question]];
 else fields=[['Aroma vocabulary',t=>t.aromas.join(', ')],['Formula',t=>DATA.live.compounds[String(t.cid)]?.formula||'Unavailable'],['Molecular weight',t=>(DATA.live.compounds[String(t.cid)]?.weight||'Unavailable')+' g/mol'],['Read the report',t=>t.tip]];
 $('#compare-content').innerHTML='<table><thead><tr><th>Compare</th>'+records.map(r=>'<th scope="col">'+safe(r.name)+'</th>').join('')+'</tr></thead><tbody>'+fields.map(([label,get])=>'<tr><th scope="row">'+label+'</th>'+records.map(r=>'<td>'+safe(get(r))+'</td>').join('')+'</tr>').join('')+'</tbody></table><p class="small" style="margin-top:20px">Descriptive information, not a quality rating or prediction of effects.</p>';$('#compare-dialog').showModal();});
$('#compare-close')?.addEventListener('click',()=>$('#compare-dialog').close());
$('#compare-dialog')?.addEventListener('click',e=>{if(e.target===$('#compare-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close();}});
function labUpdate(){
 const vals=Object.fromEntries($$('[data-lab]').map(i=>[i.dataset.lab,i.value.trim()===''?null:Number(i.value)]));
 try{const result=GuideMath.lab(vals,$('#lab-unit').value);if(!result.entered){$('#lab-result').innerHTML='<p>Enter at least one result to calculate.</p>';return result;}
 $('#lab-result').innerHTML='<p>Total of entered compounds</p><div class="big">'+result.total.toFixed(3).replace(/\.?0+$/,'')+'%</div><p>'+result.entered+' of '+DATA.terpenes.length+' fields entered. Blank values are unknown.</p>'+result.rows.map(r=>'<div class="bar-row"><div class="bar-head"><span>'+safe(DATA.terpenes.find(t=>t.id===r.id).name)+'</span><span>'+r.percent.toFixed(3)+'% · '+r.mgg.toFixed(2)+' mg/g</span></div><div class="bar"><span style="width:'+(result.total?r.percent/result.total*100:0)+'%"></span></div></div>').join('')+'<p class="units">Bars show each compound’s share of the entered total.</p>';return result;
 }catch(e){$('#lab-result').textContent=e.message;return {error:e.message};}
}
$$('[data-lab]').forEach(i=>i.addEventListener('input',labUpdate));$('#lab-unit')?.addEventListener('change',labUpdate);$('#lab-reset')?.addEventListener('click',()=>{$$('[data-lab]').forEach(i=>i.value='');labUpdate();});
function cityUpdate(){const city=DATA.cities.find(c=>c.id===$('#city').value);const covered=city&&DATA.live.delivery.cities.includes(city.name);$('#city-result').innerHTML=covered?'<p><strong>'+safe(city.name)+' is in the published service area.</strong><br>'+money(DATA.live.delivery.minimum)+' minimum · '+money(DATA.live.delivery.fee)+' published fee.<br><a href="delivery-'+city.id+'.html">Read the city guide ↗</a> · <a href="https://plpcsanjose.com/weed-delivery" rel="sponsored noopener" target="_blank">Confirm exact address ↗</a></p>':'<p><strong>Check your address with the retailer.</strong><br>This guide covers selected South Bay cities. An unlisted city is not a rejection.<br><a href="https://plpcsanjose.com/weed-delivery" rel="sponsored noopener" target="_blank">Open Purple Lotus’s address checker ↗</a></p>';return {city:city?.name||null,publishedCoverage:!!covered,exactAddressConfirmed:false};}
$('#delivery-form')?.addEventListener('submit',e=>{e.preventDefault();cityUpdate();});$('#city')?.addEventListener('change',cityUpdate);
function budgetUpdate(){
 try{if($('#subtotal').value.trim()==='')throw new Error('Enter your product subtotal.');
 const r=GuideMath.budget({subtotal:Number($('#subtotal').value),tax:$('#tax').value.trim()===''?null:Number($('#tax').value),tip:Number($('#tip').value||0),fee:DATA.live.delivery.fee,minimum:DATA.live.delivery.minimum,fulfillment:$('#fulfillment').value});
 $('#budget-result').innerHTML='<p>'+(r.preTax?'Planning subtotal, before tax':'Planning total using your entered tax')+'</p><div class="big">'+money(r.total)+'</div><p>Includes '+money(r.delivery)+' delivery fee'+(Number($('#tip').value)?' and '+money(Number($('#tip').value))+' optional tip':'')+'.</p>'+(r.belowMinimum?'<p><strong>'+money(r.gap)+' below the published delivery minimum.</strong> The retailer confirms qualification after discounts.</p>':'<p>The retailer confirms minimum qualification, final fees and taxes.</p>')+(r.preTax?'<p><strong>Tax has not been included.</strong> Add the amount from checkout for a fuller estimate.</p>':'')+'<p>This is a planning calculation, not a checkout quote.</p>';return r;
 }catch(e){$('#budget-result').textContent=e.message;return {error:e.message};}
}
['subtotal','tax','tip','fulfillment'].forEach(id=>$('#'+id)?.addEventListener('input',budgetUpdate));if($('#budget-result'))budgetUpdate();if($('#city-result'))cityUpdate();
$$('[data-check]').forEach(c=>c.addEventListener('change',()=>{const n=$$('[data-check]:checked').length;$('#check-progress').textContent=n===5?'5 of 5 ready. Confirm the final details with the retailer.':n+' of 5 ready';}));
const checked=Date.parse(DATA.live.last_success),stale=Number.isFinite(checked)&&Date.now()-checked>45*24*60*60*1000,failed=DATA.live.checks?.some(c=>c.status==='error');
if((stale||failed)&&/sources\.html$/.test(location.pathname)){const n=document.createElement('div');n.className='notice';n.textContent=stale?'These source records are more than 45 days old. Confirm current details with the original source.':'A source refresh needs review. Last successful data and its original date are shown.';$('#main').prepend(n);}
if(document.modelContext?.registerTool){
 const tools=[];
 if($('#brand-search'))tools.push({name:'filter_cannabis_brands',description:'Filter the visible brand directory by text; returns matching profile names. Does not check stock.',inputSchema:{type:'object',properties:{query:{type:'string'}},required:['query'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{if(typeof input?.query!=='string')throw new Error('query must be a string');$('#brand-search').value=input.query;updateBrands();return {matches:cards.filter(c=>!c.hidden).map(c=>c.dataset.card)};}});
 if($('#city'))tools.push({name:'check_published_delivery_city',description:'Select a city in the planner and report published coverage, not exact-address eligibility.',inputSchema:{type:'object',properties:{cityId:{type:'string',enum:DATA.cities.map(c=>c.id).concat('other')}},required:['cityId'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{if(!DATA.cities.some(c=>c.id===input?.cityId)&&input?.cityId!=='other')throw new Error('Unknown city');$('#city').value=input.cityId;return cityUpdate();}});
 if($('#lab-unit'))tools.push({name:'calculate_terpene_panel',description:'Populate the visible lab converter with provided compound values. No dose recommendations.',inputSchema:{type:'object',properties:{unit:{enum:['mgg','percent']},values:{type:'object',additionalProperties:{type:'number',minimum:0}}},required:['unit','values'],additionalProperties:false},annotations:{readOnlyHint:false},execute:input=>{if(!input?.values||typeof input.values!=='object'||Array.isArray(input.values))throw new Error('values must be an object');for(const k of Object.keys(input.values))if(!DATA.terpenes.some(t=>t.id===k))throw new Error('Unknown compound');GuideMath.lab(input.values,input.unit);$('#lab-unit').value=input.unit;$$('[data-lab]').forEach(i=>i.value=input.values[i.dataset.lab]??'');return labUpdate();}});
 for(const t of tools)try{Promise.resolve(document.modelContext.registerTool(t)).catch(()=>{});}catch{}
}
}
