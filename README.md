# Teman Mama

Free pregnancy and pantang website for Malaysian families, in English and Bahasa Melayu.
It's a static site (plain HTML, CSS and JS) that you can host free on GitHub Pages or Cloudflare Pages.
It earns money from ads (Google AdSense) and from Shopee affiliate links on the hospital-bag list.

## Pages (each in `/en/` and `/ms/`)
| Page | What it does |
|---|---|
| Home | "Which week am I?" from due date or last period |
| Week by week (4-40) | Baby size (Malaysian fruits), growth, body changes, a to-do and warning signs, one page per week |
| Pantang planner | Malay 44 / Chinese 30 / Indian 40 days or custom: dated timeline before and after the birth |
| Confinement cost | Typical 2026 prices, a 4-quote comparer (price per day, nurse ratio warning), questions to ask |
| Hospital bag | 27-item checklist saved on the phone, Shopee links |
| Maternity leave | 98-day maternity and 7-day paternity leave dates (Employment Act 1955, amended 2023) |
| Milk & diaper prices | Official government prices (KPDN PriceCatcher) by state and district, with the 5 cheapest shops |
| Taska & tadika | Google Maps search near you or by district, what to check, registration and tax-relief notes |
| About, Privacy | Disclaimer, sources, ads and affiliate disclosure |
| Feedback | Embedded Google Form ("Teman Mama feedback", answers in a Google Sheet) |
| Helper bot (every page) | "Ask Teman" button: keyword matching in EN/BM (`BOT_KW`/`BOT_ANS` in build.py), no AI; warning-sign words always get the go-to-hospital / 999 answer |

Product photos on the prices page come from Shopee's image server; the chosen photos are in `site-data/product-images.json` (none for Step 1/2 infant formula).

Nothing a visitor types leaves their phone: it's kept in the browser's local storage. There are no accounts and no server.

## Build
```
python build.py                 # writes ./site
python build.py --ad-preview    # same, with grey boxes showing where ads go
```
Preview locally: `python -m http.server 8766 --directory site`, then open http://localhost:8766

## Refresh prices
```
pip install pandas pyarrow
python scripts/update_prices.py <folder with the PriceCatcher .parquet files>
python build.py
```
Files come from https://storage.data.gov.my/pricecatcher/ (`lookup_item.parquet`, `lookup_premise.parquet`, `pricecatcher_YYYY-MM.parquet`).
On GitHub, `.github/workflows/deploy.yml` publishes the site on every push and refreshes prices every Monday.

## Before going live (edit `config.py`)
1. **Name**: "Teman Mama" is a working name. Check the trade mark register, the web address and social handles first.
2. **Web address**: buy the domain, set `BASE_URL` (turns on the sitemap and search-engine tags).
3. **Email**: set `CONTACT_EMAIL` (shows "get listed" buttons for confinement centres and taska).
4. **Ads**: apply for Google AdSense with the live site, then set `ADSENSE_CLIENT` (and `AD_SLOTS` if you make manual ad units). `ads.txt` is generated for you.
5. **Affiliate**: join the Shopee Affiliate Programme and paste your links into `AFFILIATE_LINKS`.
6. Rebuild with `python build.py` and publish the `site/` folder.

## Content rules
- General information only: no diagnosis or treatment advice; always "ask your doctor or clinic".
- No ads, affiliate links or promotion for infant formula (Step 1/2). Price information only.
