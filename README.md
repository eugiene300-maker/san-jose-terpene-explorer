# NOSE NOTES

Purple Lotus sponsored San Jose consumer resource. Static, multipage site.

Live: https://san-jose-terpene-explorer.onrender.com

## Structure

- `dist/` — the published website (HTML, local images, sitemap, RSS, llms.txt). Deployed as-is.
- `src/` — shared CSS and browser scripts, copied into `dist/assets/` by the build.
- `data/` — site config (`config.json`: site kind and canonical URL), editorial content, articles, photo credits and fetched source data.
- `scripts/` — `build.py` (static page generator, Python 3.12+), `refresh.py` (source fetcher that keeps the last good data on failure), `check.py` (HTML, link, asset and schema checks), `test-*.cjs` (Node tests).

## Commands

```
python3 scripts/refresh.py   # fetch public source data
python3 scripts/build.py     # regenerate dist/
python3 scripts/check.py     # validate pages, links, assets, schema
npm test                     # calculator and sharing tests
```

## Deployment

Live at https://san-jose-terpene-explorer.onrender.com/ on Render, which publishes `dist/` on every push to `main`. Canonical URLs, the sitemap and llms.txt use the address set in `data/config.json`; change it there and run `python3 scripts/build.py` (Python 3.12+) if the site moves.

## Content boundaries

No products are sold here. No medical recommendations, dosing instructions, live-stock claims, verified-license badges or guaranteed delivery times. Sponsor links use `rel="sponsored"`. Photo credits and licenses are listed on the Sources page and in `IMAGE-SOURCES.md`.
