"""Build crawlable topic hubs and contextual internal links from current content."""
from pathlib import Path
from html import escape, unescape
from collections import Counter
import json, re, math
STOP=set('a an the and or to of in on for with at by from is are as it its your you what how why when that this can cannabis san jose california local shoppers guide our not vs before after into about all more'.split())
def plain(s):return unescape(re.sub('<[^>]+>',' ',s))
def words(s):return [w for w in re.findall(r'[a-z]{3,}',plain(s).lower()) if w not in STOP]
def attach(out,page,kind,root):
 config=json.loads((root/'data/topics.json').read_text());topics=config['topics'];articles=json.loads((root/'data/magazine.json').read_text())['articles'];byfile={'story-'+a['id']+'.html':a for a in articles};records={}
 for p in sorted(out.glob('*.html')):
  if not (p.name.startswith(('story-','guide-','brand-','terpene-','delivery-','place-','neighborhood-','off-the-clock-')) or p.name in ['index.html','lab-report-tool.html','san-jose-field-notes.html']):continue
  html=p.read_text();main=re.search(r'<main\b[^>]*>(.*?)</main>',html,re.S).group(1)
  title=plain(re.search(r'<h1\b[^>]*>(.*?)</h1>',main,re.S).group(1)).strip()
  a=byfile.get(p.name)
  text=' '.join(a['body']) if a else plain(re.sub(r'<aside\b.*?</aside>','',main,flags=re.S))
  if a:title=a['title']
  hits=[t['id'] for t in topics if a and a['import_number'] in t['articles']]
  if not hits:
   scores=[(sum(len(re.findall(r'\b'+re.escape(k)+r'\b',title.lower()))*5+min(3,len(re.findall(r'\b'+re.escape(k)+r'\b',text.lower()))) for k in t['keywords']), t['id']) for t in topics]
   scores.sort(reverse=True);hits=[x[1] for x in scores[:2] if x[0]>0] or [topics[0]['id']]
  if p.name in ['index.html','lab-report-tool.html']:hits=config['tool_topics'].get(p.name,hits)
  records[p.name]={'title':title,'text':text,'topics':hits,'type':'Article' if a else 'Tool' if p.name in ['index.html','lab-report-tool.html'] else 'Field guide','number':a['import_number'] if a else None,'counts':Counter(words(title+' '+title+' '+text))}
 # TF-IDF makes a shared specific subject matter more than common vocabulary.
 df=Counter(w for r in records.values() for w in r['counts']);n=len(records)
 for r in records.values():
  r['vector']={w:(1+math.log(c))*math.log(1+n/(1+df[w])) for w,c in r['counts'].items()};r['norm']=math.sqrt(sum(v*v for v in r['vector'].values())) or 1
 def score(a,b):return sum(v*b['vector'].get(w,0) for w,v in a['vector'].items())/(a['norm']*b['norm'])+0.2*len(set(a['topics'])&set(b['topics']))
 def href(file,title):return '<a href="'+file+'">'+escape(title)+'</a>'
 def links(files):return '<ul class="topic-links">'+''.join('<li><small>'+records[f]['type']+'</small>'+href(f,records[f]['title'])+'</li>' for f in files)+'</ul>'
 def topicnav(ids):return '<nav class="topic-nav wrap" aria-label="Topics">'+href('topics.html','Browse topics')+''.join(href('topic-'+t['id']+'.html',t['title']) for t in topics if t['id'] in ids)+'</nav>'
 # Exact subject phrases only, preserving supplied wording and existing links.
 targets={}
 for f,r in records.items():
  aliases=config['aliases'].get(str(r['number']),[]) if r['number'] else []
  if f.startswith('terpene-'):
   aliases+=[r['title'].split(':')[0]]
  if f.startswith('brand-'):
   for b in json.loads((root/'data/editorial.json').read_text())['brands']:
    if f=='brand-'+b['id']+'.html':aliases+=[b['name']]
  for phrase in aliases:
   if len(phrase)>3:targets.setdefault(phrase.lower(),f)
 pattern=re.compile(r'(?<!\w)('+ '|'.join(re.escape(x) for x in sorted(targets,key=len,reverse=True))+r')(?!\w)',re.I) if targets else None
 audit={}
 for file,r in records.items():
  html=(out/file).read_text();html=re.sub(r'<section class="section"><div class="wrap"><h2>Related reading</h2>.*?</section>','',html,flags=re.S)
  used=set();inline_count=[0]
  def para(match):
   parts=re.split(r'(<[^>]+>)',match.group(0));depth=0
   for i,part in enumerate(parts):
    if part.startswith('<a '):depth+=1
    elif part.startswith('</a'):depth=max(0,depth-1)
    elif not part.startswith('<') and depth==0 and inline_count[0]<4 and pattern:
     def replace(m):
      target=targets[m.group(0).lower()]
      if target==file or target in used or inline_count[0]>=4:return m.group(0)
      used.add(target);inline_count[0]+=1
      return '<a class="context-link" href="'+target+'">'+m.group(0)+'</a>'
     parts[i]=pattern.sub(replace,part,count=1)
   return ''.join(parts)
  # Restrict inline changes to article prose; never alter ads, sources or controls.
  region=re.search(r'(<div class="mag-prose">)(.*?)(<div class="article-sharing">)',html,re.S) or re.search(r'(<article class="article">)(.*?)(</article>)',html,re.S)
  if region:
   prose=re.sub(r'<(?:p|li)\b[^>]*>.*?</(?:p|li)>',para,region.group(2),flags=re.S)
   html=html[:region.start(2)]+prose+html[region.end(2):]
  candidates=sorted((f for f in records if f!=file), key=lambda f:(-score(r,records[f]),f))
  related=[]
  # Include the useful tool/guide alongside reporting when available.
  for want in ['Article','Article','reference']:
   match=next((f for f in candidates if f not in related and set(records[f]['topics'])&set(r['topics']) and ((records[f]['type']=='Article') if want=='Article' else records[f]['type']!='Article')),None)
   if match:related.append(match)
  section='<section class="topic-reading wrap" aria-label="Related reading"><h2>Related reading</h2>'+links(related)+'</section>'
  if file=='index.html':
   html=html.replace('</main>',topicnav([t['id'] for t in topics])+section+'</main>')
  else:
   html=re.sub(r'(<main\b[^>]*>)',lambda m:m.group(1)+topicnav(r['topics']),html,count=1)
   marker='<aside class="business-spotlight wrap"'
   html=html.replace(marker,section+marker,1) if marker in html else html.replace('</main>',section+'</main>')
  (out/file).write_text(html);audit[file]={'topics':r['topics'],'contextual_links':sorted(used),'related':related}
 for t in topics:
  files=[f for f,r in records.items() if t['id'] in r['topics']]
  body='<section class="subhero"><div class="wrap"><p class="eyebrow">'+href('topics.html','Topics')+'</p><h1>'+escape(t['title'])+'</h1><p>'+escape(t['description'])+'</p></div></section>'
  for label,isarticle in [('Tools and field guides',False),('Stories',True)]:
   subset=[f for f in files if (records[f]['type']=='Article')==isarticle]
   if subset:body+='<section class="section"><div class="wrap"><h2>'+label+'</h2>'+links(subset)+'</div></section>'
  body+=topicnav([x['id'] for x in topics if x!=t])
  page('topic-'+t['id']+'.html',t['title'],t['description'],body,schema={'@type':'CollectionPage'})
 body='<section class="subhero"><div class="wrap"><p class="eyebrow">Explore</p><h1>Browse by topic</h1><p>Find the stories, guides and tools for the question on your mind.</p></div></section><section class="section"><div class="wrap topic-index">'+''.join('<article><h2>'+href('topic-'+t['id']+'.html',t['title'])+'</h2><p>'+escape(t['description'])+'</p></article>' for t in topics)+'</div></section>'
 page('topics.html','Browse by topic','Articles, guides and tools organized by subject.',body,schema={'@type':'CollectionPage'})
 # Every site page exposes the topic hub through ordinary HTML navigation.
 for p in out.glob('*.html'):
  html=p.read_text();html=re.sub(r'(<a href="journal.html"[^>]*>Journal</a>)',r'\1<a href="topics.html">Topics</a>',html)
  if p.name in ['journal.html','guides.html']:
   html=html.replace('</main>',topicnav([t['id'] for t in topics])+'</main>')
  p.write_text(html)
 (out/'topic-links.json').write_text(json.dumps(audit,indent=2))
 return audit
