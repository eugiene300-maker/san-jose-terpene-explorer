"""Validate generated pages, local links, images, schema, and sponsor references."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,subprocess
R=Path(__file__).resolve().parents[1];D=R/'dist';errors=[]
class Check(HTMLParser):
 def __init__(self):super().__init__();self.refs=[];self.h1=0;self.title=False;self.meta=False;self.ids=[];self.jsons=[];self.script=False;self.buf='';self.sponsor=0
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='h1':self.h1+=1
  if t=='title':self.title=True
  if t=='meta' and a.get('name')=='description':self.meta=True
  if a.get('id'):self.ids.append(a['id'])
  if t in ('a','link','img','script'):
   ref=a.get('href') or a.get('src')
   if ref:self.refs.append(ref)
  if t=='a' and 'plpcsanjose.com' in a.get('href','') and 'sponsored' in a.get('rel',''):self.sponsor+=1
  if t=='script' and a.get('type') in ('application/ld+json','application/json'):self.script=True;self.buf=''
 def handle_data(self,d):
  if self.script:self.buf+=d
 def handle_endtag(self,t):
  if t=='script' and self.script:
   try:json.loads(self.buf)
   except Exception as e:errors.append('Invalid embedded JSON: '+str(e))
   self.script=False
pages=list(D.glob('*.html'))
for p in pages:
 c=Check();c.feed(p.read_text())
 if c.h1!=1 or not c.title or not c.meta:errors.append(f'{p.name}: heading or metadata missing')
 if len(c.ids)!=len(set(c.ids)):errors.append(p.name+': duplicate IDs')
 if not c.sponsor:errors.append(p.name+': no qualified sponsor link')
 for ref in c.refs:
  url=urlsplit(ref)
  if url.scheme or url.netloc or not url.path:continue
  if not (D/unquote(url.path)).exists():errors.append(f'{p.name}: missing {ref}')
for needed in ['sitemap.xml','robots.txt','llms.txt','data.json']:
 if not (D/needed).is_file():errors.append('Missing '+needed)
for f in ['app.js','experience.js']:subprocess.run(['node','--check',str(R/'src'/f)],check=True)
if errors:raise SystemExit('\n'.join(errors))
print(json.dumps({'validated_pages':len(pages),'local_links':'passed','images':'passed','schema':'passed','javascript':'passed'}))
