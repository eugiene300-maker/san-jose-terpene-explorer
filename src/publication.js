document.querySelectorAll('[data-story-share]').forEach(button=>button.addEventListener('click',async()=>{const status=button.parentElement.querySelector('.story-share-status');const url=document.querySelector('link[rel="canonical"]')?.href||location.href;const title=document.querySelector('h1')?.textContent||document.title;try{if(navigator.share)await navigator.share({title,url});else {await navigator.clipboard.writeText(url);status.textContent='Story link copied.';}}catch(error){if(error.name!=='AbortError'){status.textContent=url;}}}));

// Suggestions come from the same published data as the tools.
document.addEventListener('DOMContentLoaded', () => {
  const data = JSON.parse(document.getElementById('site-data').textContent);
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  function suggest(input, entries, choose) {
    if (!input) return;
    const wrapper = document.createElement('div'); wrapper.className = 'typeahead';
    input.before(wrapper); wrapper.append(input);
    const list = document.createElement('ul'); list.id = input.id + '-suggestions';
    list.className = 'typeahead-list'; list.role = 'listbox'; list.hidden = true;
    wrapper.append(list);
    const status = document.createElement('span'); status.className = 'sr-only';
    status.setAttribute('role', 'status'); wrapper.append(status);
    input.setAttribute('role', 'combobox'); input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-controls', list.id); input.setAttribute('aria-expanded', 'false');
    input.setAttribute('autocomplete', 'off');
    let matches = [], active = -1;
    function close() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); active = -1; }
    function pick(index) {
      const entry = matches[index]; if (!entry) return;
      input.value = entry.label; choose(entry); close(); input.focus();
      status.textContent = entry.label + ' selected.';
    }
    function render() {
      const query = normalize(input.value);
      matches = entries.filter(item => normalize(item.label + ' ' + (item.search || '')).includes(query))
        .sort((a,b) => Number(normalize(b.label).startsWith(query)) - Number(normalize(a.label).startsWith(query))).slice(0, 7);
      list.replaceChildren(); active = -1; input.removeAttribute('aria-activedescendant');
      matches.forEach((item, index) => {
        const option = document.createElement('li'); option.id = list.id + '-' + index;
        option.role = 'option'; option.setAttribute('aria-selected', 'false');
        const title = document.createElement('span'); title.textContent = item.label; option.append(title);
        if (item.detail) { const detail = document.createElement('small'); detail.textContent = item.detail; option.append(detail); }
        option.addEventListener('pointerdown', event => event.preventDefault());
        option.addEventListener('click', () => pick(index)); list.append(option);
      });
      list.hidden = !matches.length; input.setAttribute('aria-expanded', String(matches.length > 0));
      status.textContent = matches.length ? matches.length + ' suggestions available. Use up and down arrows to choose.' : 'No matching suggestions.';
    }
    input.addEventListener('input', render); input.addEventListener('focus', render);
    input.addEventListener('keydown', event => {
      if (event.isComposing) return;
      if (event.key === 'Escape') { close(); return; }
      if (event.key === 'Tab') { close(); return; }
      if (event.key === 'Enter' && !list.hidden && active >= 0) { event.preventDefault(); pick(active); return; }
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      event.preventDefault(); if (list.hidden) render(); if (!matches.length) return;
      active = (active + (event.key === 'ArrowDown' ? 1 : (active < 0 ? 0 : -1)) + matches.length) % matches.length;
      [...list.children].forEach((option, index) => option.setAttribute('aria-selected', String(index === active)));
      input.setAttribute('aria-activedescendant', list.children[active].id);
      list.children[active].scrollIntoView({block: 'nearest'});
    });
    input.addEventListener('blur', close);
    document.addEventListener('pointerdown', event => { if (!wrapper.contains(event.target)) close(); });
  }
  const brand = document.getElementById('brand-search');
  if (brand) {
    const entries = data.brands.map(item => ({label:item.name, detail:'Brand · ' + item.region, search:item.formats.join(' ')}));
    [...new Set(data.brands.flatMap(item => item.formats))].forEach(label => entries.push({label,detail:'Product format'}));
    [...new Set(data.brands.map(item => item.region))].forEach(label => entries.push({label,detail:'Brand origin'}));
    suggest(brand, entries, () => brand.dispatchEvent(new Event('input', {bubbles:true})));
  }
  const glossary = document.getElementById('glossary-search');
  if (glossary) suggest(glossary, [...document.querySelectorAll('[data-term]')].map(item => ({label:item.querySelector('summary').textContent.trim(), search:item.dataset.term,detail:'Glossary'})), () => glossary.dispatchEvent(new Event('input', {bubbles:true})));
  const city = document.getElementById('city');
  if (city) {
    const input = document.createElement('input'); input.type = 'search'; input.id = 'city-search'; input.placeholder = 'Start typing a city…';
    input.value = city.value === 'other' ? '' : city.selectedOptions[0].textContent;
    city.before(input); city.hidden = true;
    document.querySelector('label[for="city"]')?.setAttribute('for', input.id);
    let typing = false;
    const entries = [...city.options].filter(option => option.value !== 'other').map(option => ({label:option.textContent, value:option.value, detail:'City guide'}));
    input.addEventListener('input', () => {
      const match = entries.find(entry => normalize(entry.label) === normalize(input.value));
      typing = true; city.value = match?.value || 'other'; city.dispatchEvent(new Event('change', {bubbles:true})); typing = false;
    });
    city.addEventListener('change', () => { if (!typing) input.value = city.value === 'other' ? '' : city.selectedOptions[0].textContent; });
    suggest(input, entries, entry => { city.value = entry.value; city.dispatchEvent(new Event('change', {bubbles:true})); });
  }
});
