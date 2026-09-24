"""Monthly public-data refresh. Standard library only; retain last good data on failure."""
import json,re,os,sys,urllib.request,datetime,copy
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'SanJoseConsumerGuides/1.0 (+public source reference; monthly refresh)'})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read().decode('utf-8')
def amount(text,pattern):
 m=re.search(pattern,text,re.I)
 if not m:raise ValueError('Published policy pattern missing; retaining prior record')
 v=float(m.group(1))
 if not 0<=v<=1000:raise ValueError('Policy value outside validation range')
 return v
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
live=json.loads((ROOT/'data/live.json').read_text());editorial=json.loads((ROOT/'data/editorial.json').read_text());kind=json.loads((ROOT/'data/config.json').read_text())['kind'];checks=[];success=0
before=copy.deepcopy(live)
live.pop('brand_listing',None);live.pop('delivery',None)
if kind=='atlas':
 from concurrent.futures import ThreadPoolExecutor
 def check_brand(b):
  try:
   raw=fetch(b['source'])
   if len(raw)<200:raise ValueError('Source response too short')
   return {'source':b['source'],'status':'ok','checked_at':now,'fields':b['name']+' official reference reachable'}
  except Exception as error:return {'source':b['source'],'status':'error','checked_at':now,'fields':b['name']+' official reference','message':str(error)}
 with ThreadPoolExecutor(max_workers=4) as pool:checks.extend(pool.map(check_brand,editorial['brands']))
 success+=sum(c['status']=='ok' for c in checks)
if kind=='terpenes':
 try:
  ids=','.join(str(t['cid']) for t in editorial['terpenes']);url=f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{ids}/property/MolecularFormula,MolecularWeight/JSON'
  data=json.loads(fetch(url))['PropertyTable']['Properties']
  if len(data)!=len(editorial['terpenes']):raise ValueError('Incomplete compound response')
  for d in data:
   if not d.get('MolecularFormula') or not 50<float(d['MolecularWeight'])<500:raise ValueError('Invalid compound record')
  live['compounds']={str(d['CID']):{'formula':d['MolecularFormula'],'weight':str(d['MolecularWeight']),'checked_at':now} for d in data}
  checks.append({'source':url,'status':'ok','checked_at':now,'fields':'Molecular formula and molecular weight'});success+=1
 except Exception as e:checks.append({'source':'https://pubchem.ncbi.nlm.nih.gov/','status':'error','checked_at':now,'message':str(e)})
if kind=='delivery':
 try:
  url='https://www.sjpd.org/about-us/organization/chief-executive-officer/cannabis-regulation/registered-cannabis-businesses'
  raw=fetch(url)
  if 'Elemental' not in raw:raise ValueError('Municipal list needs editorial review; no business records changed')
  checks.append({'source':url,'status':'ok','checked_at':now,'fields':'Municipal business reference reachable'});success+=1
 except Exception as e:checks.append({'source':'https://www.sjpd.org/about-us/organization/chief-executive-officer/cannabis-regulation/registered-cannabis-businesses','status':'error','checked_at':now,'message':str(e)})
def facts(v):
 if isinstance(v,dict):return {k:facts(x) for k,x in v.items() if k!='checked_at'}
 if isinstance(v,list):return [facts(x) for x in v]
 return v
changed=[k for k in ['delivery','brand_listing','compounds'] if facts(before.get(k))!=facts(live.get(k))]
history=live.get('history',[])
history.insert(0,{'checked_at':now,'changed_fields':changed,'failed_sources':[c['source'] for c in checks if c['status']=='error']})
live['history']=history[:24]
live['checks']=checks;live['last_attempt']=now
if success:live['last_success']=now
p=ROOT/'data/live.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(live,indent=2));os.replace(tmp,p)
print(json.dumps({'kind':kind,'successful_sources':success,'checks':checks}))
if any(c['status']=='error' for c in checks):sys.exit(1)
