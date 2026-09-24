"""Magazine publishing layer: distinct desks, dated notebooks, linked author archives."""
from html import escape as e
from pathlib import Path
import json,re,datetime,math,email.utils
ROOT=Path(__file__).resolve().parents[1]
_TOOL_HOME=''
def data():return json.loads((ROOT/'data/magazine.json').read_text())
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def url(a):return 'story-'+a['id']+'.html'
def author_link(name):return '<a rel="author" href="author-'+slug(name)+'.html">'+e(name)+'</a>'
def stamp(d):return datetime.date.fromisoformat(d).strftime('%B %d, %Y').replace(' 0',' ')
def inline(text):
 text=e(text)
 text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
 text=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',text)
 return text

def paragraph(text):
 if text.startswith('## '):return '<h2>'+inline(text[3:])+'</h2>'
 lines=text.splitlines()
 if all(re.match(r'^\d+\. ',x) for x in lines):return '<ol>'+''.join('<li>'+inline(re.sub(r'^\d+\. ','',x))+'</li>' for x in lines)+'</ol>'
 if all(re.match(r'^[-*] ',x) for x in lines):return '<ul>'+''.join('<li>'+inline(x[2:])+'</li>' for x in lines)+'</ul>'
 return '<p>'+inline(text)+'</p>'

def photo(a,cls=''):
 p=json.loads((ROOT/'data/local-photos.json').read_text())[a.get('photo','downtown')]
 src=p['file'];thumb=p.get('thumb',src)
 attrs=(' srcset="assets/'+thumb+' 480w, assets/'+src+' 1280w" sizes="(max-width:700px) 100vw, '+('45vw' if cls=='mag-cover' else '80vw')+'"') if thumb!=src else ''
 credit=p.get('author','');caption=p.get('caption',p['alt'])
 return '<figure class="mag-photo '+cls+'"><img src="assets/'+src+'"'+attrs+' alt="'+e(p['alt'],quote=True)+'" loading="lazy" width="1280" height="720"><figcaption>'+e(caption)+' · '+e(credit)+' · <a href="'+e(p.get('source','sources.html#local-photography'),quote=True)+'" target="_blank" rel="noopener">Image source</a></figcaption></figure>'
def cards(articles):
 return '<div class="mag-cards">'+''.join('<article class="mag-card"><a class="mag-thumb" href="'+url(a)+'">'+re.sub(r'<figcaption>.*?</figcaption>','',photo(a))+'</a><p class="eyebrow">'+e(a['beat'])+' / '+e(a['type'])+'</p><h3><a href="'+url(a)+'">'+e(a['title'])+'</a></h3><p>'+e(a['dek'])+'</p><div class="mag-meta">'+author_link(a['author'])+'<span>'+stamp(a['topic_date'])+'</span></div></article>' for a in articles)+'</div>'
def business_card(kind, business='purple-lotus'):
 if business=='purple-lotus':
  target='https://plpcsanjose.com/weed-delivery' if kind=='delivery' else 'https://plpcsanjose.com/'
  name='Purple Lotus Weed Delivery in San Jose' if kind=='delivery' else 'Purple Lotus Cannabis Dispensary'
  description='Cannabis delivery in San Jose. Check current service areas and availability.' if kind=='delivery' else 'Cannabis dispensary with Commercial Street and downtown San Jose locations.'
  heading='<a href="'+target+'" rel="sponsored noopener" target="_blank">'+name+'</a>'
  image='business-purple-lotus.webp';alt='Purple Lotus dispensary exterior in San Jose';category='DISPENSARY';label='<span class="business-sponsored">Sponsored</span>';attrs=' aria-label="Publication sponsor"'
 else:
  b=next(b for b in json.loads((ROOT/'data/featured-businesses.json').read_text())['businesses'] if b.get('id')==business)
  heading=e(b['name']);category=b['category'].upper();description=b['description'];image=b['image'];alt=b['alt'];label='';attrs=''
 return '<article class="business-card"'+attrs+'><img class="business-photo" src="assets/'+image+'" alt="'+e(alt,quote=True)+'" width="600" height="360" loading="lazy"><div class="business-copy"><div class="business-category"><span>'+category+'</span>'+label+'</div><h3>'+heading+'</h3><p>'+description+'</p></div></article>'

def advert(kind):
 return '<aside class="business-spotlight wrap" aria-label="Featured San Jose business">'+business_card(kind)+'</aside>'

def featured_businesses(kind):
 return '<section class="local-businesses wrap" aria-labelledby="featured-businesses-title"><h2 id="featured-businesses-title">Featured San Jose businesses</h2><div class="business-grid">'+''.join(business_card(kind,b) for b in ['purple-lotus']+[b['id'] for b in json.loads((ROOT/'data/featured-businesses.json').read_text())['businesses'] if not b.get('sponsored')])+'</div></section>'

def front(kind):
 d=data();articles=sorted(d['articles'],key=lambda a:a['published'],reverse=True);lead=articles[0]
 return '<section class="mag-front wrap"><div class="mag-mastline"><span>'+e(d['strap'])+'</span><a href="journal.xml">RSS ↗</a></div><div class="mag-lead"><div class="mag-lead-copy"><p class="eyebrow">'+e(lead['beat'])+' / '+e(lead['type'])+'</p><h1><a href="'+url(lead)+'">'+e(lead['title'])+'</a></h1><p class="mag-dek">'+e(lead['dek'])+'</p><div class="mag-meta">By '+author_link(lead['author'])+'<span>'+str(math.ceil(len(' '.join(lead['body']).split())/220))+' min read</span></div><a class="mag-read" href="'+url(lead)+'">Read the story ↗</a></div>'+photo(lead,'mag-cover')+'</div><div class="mag-tool"><span>'+e(d['tool']['eyebrow'])+'</span><h2>'+e(d['tool']['title'])+'</h2><p>'+e(d['tool']['text'])+'</p><a class="btn dark" href="'+d['tool']['url']+'">'+e(d['tool']['label'])+' ↗</a></div></section>'+'<section class="section"><div class="wrap"><div class="section-head"><div><p class="eyebrow">FROM THE JOURNAL</p><h2>'+e(d['section_title'])+'</h2></div><a href="journal.html">All stories ↗</a></div>'+cards(articles[1:])+'</div></section>'
def transform(file,body,kind):
 global _TOOL_HOME
 d=data()
 if file=='brands.html' and kind=='atlas':_TOOL_HOME=body
 if file=='index.html':
  if kind=='atlas':body=_TOOL_HOME
  pos=body.find('</section>')+len('</section>')
  body=body[:pos]+featured_businesses(kind)+body[pos:]
  return body+'<section class="section"><div class="wrap"><p class="eyebrow">THE JOURNAL</p><h2>More from '+e(d['name'])+'</h2><p>'+e(d['strap'])+'</p><a class="btn dark" href="journal.html">Read the journal ↗</a></div></section>'
 if file=='team.html':
  return '<section class="subhero"><div class="wrap"><p class="eyebrow">'+e(d['name'])+'</p><h1>'+e(d['team_title'])+'</h1><p>'+e(d['team_intro'])+'</p></div></section><section class="section"><div class="wrap team-grid">'+''.join('<article class="team-card"><span class="team-monogram">'+''.join(x[0] for x in p['name'].split())+'</span><p class="eyebrow">'+e(p['beat'])+'</p><h2>'+author_link(p['name'])+'</h2><p>'+e(p['bio'])+'</p><a href="author-'+slug(p['name'])+'.html">Read '+e(p['name'].split()[0])+'’s stories ↗</a></article>' for p in d['authors'])+'</div></section>'
 if file=='about.html':
  return '<section class="subhero"><div class="wrap"><p class="eyebrow">ABOUT '+e(d['name'])+'</p><h1>'+e(d['about_title'])+'</h1><p>'+e(d['strap'])+'</p></div></section><section class="section"><div class="wrap article">'+''.join('<p>'+e(p)+'</p>' for p in d['about'])+'<h2>Start here</h2><p><a href="journal.html">Read the latest stories</a> · <a href="team.html">Meet the editorial team</a> · <a href="editorial-standards.html">Editorial policy</a></p></div></section>'
 if file=='editorial-standards.html':
  return '<section class="subhero"><div class="wrap"><p class="eyebrow">EDITORIAL POLICY</p><h1>A point of view. A few firm rules.</h1></div></section><section class="section"><div class="wrap article"><h2>The story comes first</h2><p>We cover the places, ideas and decisions that matter to our readers. Advertising is labeled and sold separately from editorial coverage. An ad does not buy a recommendation, a ranking or a place in a story.</p><h2>Facts and opinion</h2><p>Our writers make arguments. Dates, locations, prices and other checkable details still need evidence. Essays and commentary are labeled; a preview is not a review. Interview material and exclusive reporting from other outlets receive credit when used.</p><h2>Dates and corrections</h2><p>Check article and event dates before relying on a schedule or offer. Material changes receive an update date. Past events stay in the archive. Send a correction through the source or contact route shown on the relevant page when available.</p><h2>Tools</h2><p>Comparisons use the inputs shown. A blank value is not a hidden estimate. Source checks flag changes for review and retain the last valid data if a source fails. Tools do not verify live stock, predict personal effects or place orders.</p><h2>Photography</h2><p>Location photos identify the place shown. They are not represented as photographs of an event we did not attend. Image credits and licenses appear in the photo details.</p></div></section>'
 # Add a useful author identity to legacy editorial guides, without invented experience.
 if file.startswith(('guide-','brand-','terpene-','neighborhood-','place-','off-the-clock-')) or file=='san-jose-field-notes.html':
  person=d['authors'][0 if file.startswith(('brand-','terpene-')) else 1]['name']
  body=body.replace('</h1>','</h1><p class="mag-meta">By '+author_link(person)+'</p>',1)
 return body

def build(page,out,urlbase,kind):
 d=data();articles=sorted(d['articles'],key=lambda a:a['published'],reverse=True)
 page('journal.html',d['name']+' journal',d['strap'],front(kind),'journal.html')
 for p in d['authors']:
  page('author-'+slug(p['name'])+'.html',p['name']+' | '+p['beat'],p['bio'],'<section class="subhero"><div class="wrap"><p class="eyebrow">'+e(p['beat'])+'</p><h1>'+e(p['name'])+'</h1><p>'+e(p['bio'])+'</p></div></section><section class="section"><div class="wrap">'+cards([a for a in articles if a['author']==p['name']])+'</div></section>')
 for a in articles:
  words=len(' '.join(a['body']).split());content=''
  for p in a['body']:
   content+=paragraph(p)
  refs=''.join('<li><a href="'+e(r[1],quote=True)+'" target="_blank" rel="noopener noreferrer">'+e(r[0])+' ↗</a></li>' for r in a['sources'])
  body='<article class="mag-story"><header class="mag-story-head wrap"><p class="eyebrow">'+e(a['beat'])+' / '+e(a['type'])+'</p><h1>'+e(a['title'])+'</h1><p class="mag-dek">'+e(a['dek'])+'</p><div class="mag-meta">By '+author_link(a['author'])+'<span>'+str(math.ceil(words/220))+' min read</span><time datetime="'+a['published']+'">'+stamp(a['published'])+'</time></div></header><div class="wrap">'+photo(a)+'</div><div class="mag-story-layout wrap"><div class="mag-prose">'+content+'<div class="article-sharing"><button class="btn dark" data-story-share>Share this story ↗</button><span class="story-share-status" role="status"></span></div><details class="mag-references"><summary>Addresses, schedules & further reading</summary><ul>'+refs+'</ul></details><div class="mag-author-end">'+author_link(a['author'])+'<p>'+e(next(p['bio'] for p in d['authors'] if p['name']==a['author']))+'</p></div></div></div></article><section class="section"><div class="wrap"><h2>Related reading</h2>'+cards([x for x in articles if x['id']!=a['id']][:3])+'</div></section>'
  schema={'@type':'Article','headline':a['title'],'datePublished':a['published'],'dateModified':a.get('updated',a['published']),'author':{'@type':'Person','name':a['author'],'url':urlbase+'/author-'+slug(a['author'])+'.html'},'publisher':{'@type':'Organization','name':d['name'],'url':urlbase},'articleSection':a['beat'],'wordCount':words,'citation':[r[1] for r in a['sources']],'image':urlbase+'/assets/'+json.loads((ROOT/'data/local-photos.json').read_text())[a['photo']]['file']}
  page(url(a),a['title'],a['dek'],body,schema=schema)
 items=''.join('<item><title>'+e(a['title'])+'</title><link>'+urlbase+'/'+url(a)+'</link><guid isPermaLink="true">'+urlbase+'/'+url(a)+'</guid><pubDate>'+email.utils.format_datetime(datetime.datetime.fromisoformat(a['published']).replace(tzinfo=datetime.timezone.utc))+'</pubDate><description>'+e(a['dek'])+'</description></item>' for a in articles)
 (out/'journal.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>'+e(d['name'])+'</title><link>'+urlbase+'</link><description>'+e(d['strap'])+'</description>'+items+'</channel></rss>')
