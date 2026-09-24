from html import escape as e

COPY={
 'atlas':{
  'kicker':'SAN JOSE IS THE STARTING POINT', 'title':'A CITY WITH<br>ITS OWN FREQUENCY.',
  'intro':'The Bay is bigger than a brand name. San Pedro Square, Japantown, and downtown each tell a different San Jose story. This is the place behind our reading of California cannabis culture.',
  'cards':[
   ('san-pedro','SAN PEDRO SQUARE','A meeting point. Not a mood board.','San Pedro Square puts food, gathering places, and downtown history in the same frame. Local culture is made by the people and places around a product, not just the name on its label.','https://www.sanjose.org/neighborhoods/downtown'),
   ('japantown','JACKSON STREET / JAPANTOWN','Roots deserve a closer look.','Japantown has its own cultural history and identity. That same attention to place matters when reading cannabis brands: founded in California, grown in California, and sold in San Jose are different claims.','https://www.sanjose.org/neighborhoods/japantown'),
   ('downtown','DOWNTOWN SAN JOSE','The city behind the shelf.','SoFA is downtown’s arts and entertainment district. Our brand directory takes a similarly curious approach to culture: learn who made it, where it comes from, and what the name actually means.','https://www.sanjose.org/listings/sofa-district')],
  'note':'These photographs document San Jose places. They do not imply that the venues sell cannabis, endorse this guide, or permit consumption.',
  'link':'Read the San Jose field notes ↗'},
 'terpenes':{
  'kicker':'TRAIN YOUR NOSE / SAN JOSE EDITION', 'title':'A CITY YOU CAN<br>GET A NOSE FOR.',
  'intro':'Start with something familiar. A garden. Fresh herbs. A bright citrus peel. San Jose gives your aroma vocabulary a place to begin, before you ever look at a terpene panel.',
  'cards':[
   ('rose-garden','MUNICIPAL ROSE GARDEN','Floral starts somewhere real.','San Jose’s Municipal Rose Garden is devoted to roses. Notice how one bloom can smell different from another. “Floral” is a useful beginning, not a complete description or a laboratory result.','https://www.sanjose.org/listings/municipal-rose-garden'),
   ('japantown','JAPANTOWN / JACKSON STREET','Your memory has a scent library.','A familiar neighborhood can bring back food, tea, wood, or spice memories. Use your own associations to describe an aroma. The photograph marks a place, not a claim about what you will smell there.','https://www.sanjose.org/neighborhoods/japantown'),
   ('san-pedro','SAN PEDRO SQUARE','Put it into your own words.','Food vocabulary gives you a useful starting point: citrus zest, pepper, herbs, toasted notes. Keep the words that fit your experience, then explore those families in the scent-signature tool.','https://www.sanjose.org/neighborhoods/downtown')],
  'note':'A sensory exercise, not a chemical analysis. A photograph or familiar aroma cannot verify a terpene or predict cannabis effects.',
  'link':'Explore the San Jose scent notebook ↗'},
 'delivery':{
  'kicker':'LOCAL CONTEXT / THE 408', 'title':'SAME CITY.<br>YOUR OWN RHYTHM.',
  'intro':'San Jose has a going-out side and a staying-in side. Our local notebook brings the city into the picture while keeping your neighborhood, the published city coverage, and your exact address distinct.',
  'cards':[
   ('downtown','DOWNTOWN SAN JOSE','The city turns the lights on.','Downtown connects San Jose’s music, art, food, and nightlife. STAY IN is the quieter companion: read the details, understand the assumptions, and decide what fits your own evening.','https://www.sanjose.org/neighborhoods/downtown'),
   ('japantown','JAPANTOWN / JACKSON STREET','A neighborhood is not an address check.','Japantown is part of San Jose, with a distinct cultural identity. A city-level listing is useful context, but it cannot confirm a particular building, entry arrangement, or available delivery window.','https://www.sanjose.org/neighborhoods/japantown'),
   ('san-pedro','SAN PEDRO SQUARE','Make room for the whole evening.','San Pedro Square is one of downtown’s gathering places. Whether your plans stay out or wind down at home, the planner keeps product amounts, entered taxes, fees, and optional tips visible as separate lines.','https://www.sanjose.org/neighborhoods/downtown')],
  'note':'Local photography is atmosphere, not a live service map. Pictured places are not represented as delivery destinations or cannabis consumption venues.',
  'link':'Open the San Jose local notebook ↗'}
}

def local_section(kind,photos):
 c=COPY[kind]
 cards=''
 for ident,label,title,desc,url in c['cards']:
  ph=photos[ident]
  cards+=f'<article class="local-card"><figure><img src="assets/{ph["file"]}" alt="{e(ph["alt"],quote=True)}" loading="lazy" width="1000" height="700"><figcaption>{label}</figcaption></figure><div class="local-card-copy"><h3>{title}</h3><p>{desc}</p><a class="local-ref" href="{url}" target="_blank" rel="noopener noreferrer">About this place ↗</a></div></article>'
 return f'<section class="section local-scenes" id="san-jose"><div class="wrap"><div class="local-intro"><div><p class="eyebrow">{c["kicker"]}</p><h2>{c["title"]}</h2></div><div><p>{c["intro"]}</p><a href="san-jose-field-notes.html">{c["link"]}</a></div></div><div class="local-grid">{cards}</div><p class="local-note">{c["note"]} <a href="sources.html#local-photography">Photo credits</a>.</p></div></section>'

def local_article(kind,photos):
 c=COPY[kind];photo=photos['rose-garden' if kind!='terpenes' else 'downtown']
 body=f'<figure class="local-panorama"><img src="assets/{photo["file"]}" alt="{e(photo["alt"],quote=True)}" width="1400" height="700"><figcaption>{e(photo["alt"])}</figcaption></figure><section class="section"><div class="wrap article"><p>{c["intro"]}</p>'
 for _,label,title,desc,url in c['cards']:
  body+=f'<h2>{title}</h2><p>{desc}</p><p><a href="{url}" target="_blank" rel="noopener noreferrer">Explore {label.title()} with Visit San Jose ↗</a></p>'
 extra={
 'atlas':('Local is a question worth asking.','Our atlas uses San Jose as its starting point, rather than treating every listed company as Bay Area-grown. Check the origin field, follow the official reference, and separate company history from the details of an individual product. A familiar neighborhood or a California story is not proof of where a particular batch was cultivated. The directory and comparison tool keep those questions close to the profile.','index.html#directory','Explore the brand roster'),
 'terpenes':('Take a note before you take a guess.','Try a simple scent notebook: write the first familiar thing an aroma reminds you of, then add a second, more specific word. Instead of just “citrus,” you might write “fresh peel” or “sweet orange.” These are personal descriptors, not chemical measurements. Choose up to three aroma families in Nose Notes, and use the lab-report converter only when you have actual numbers from a report.','index.html#scent-studio','Build your scent signature'),
 'delivery':('A neighborhood name is only the beginning.','The planner uses published city coverage and the amounts you enter. It does not determine building access, reserve a delivery window, or establish a final checkout amount. Keep the estimate as a planning snapshot. If you share it, the link carries the selected city and numbers, not your street address. Local context should make information easier to understand without pretending to know more about your home than you have supplied.','index.html#planner','Return to the planner')}
 title,para,href,label=extra[kind]
 body+=f'<h2>{title}</h2><p>{para}</p><p><a class="btn dark" href="{href}">{label} ↗</a></p><p class="small">{c["note"]} Photographs and local references are documented in <a href="sources.html#local-photography">our sources</a>.</p></div></section>'
 return body
