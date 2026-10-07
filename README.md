# Naver Map, Shopping & Blog Scraper — Python Example (네이버 크롤러)

> Scrape Naver Map places with reviews and menus, Naver Shopping products with sellers, Naver Blog, Cafe and News posts, real-estate listings and BEST rankings from Python — no Naver Open API keys, no login, no Korean proxies to buy.

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-blue)](https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

A ready-to-run Python project around the [Naver Scraper API Apify actor](https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python). One actor, one input format, **18 Naver data sources** — from 네이버 지도 places and 스마트스토어 reviews to 블로그, 카페, 뉴스, 지식iN, 네이버 부동산 and DataLab shopping trends.

## What this does

Naver is where South Korea searches. Google barely matters there: restaurants live on Naver Map, sellers live on Smart Store, and consumer opinion lives in Naver Blog and Naver Cafe. If you do market research, local SEO or e-commerce in Korea, that data is the ground truth.

The official Naver Open API is a poor fit for it. You need a registered application with a client ID and secret, you get a daily quota, and the responses are short search snippets — no visitor reviews, no menus, no seller details, no comments, no real-estate listings. This repository shows how to get all of that through a single HTTP call to an Apify actor that reads Naver's public pages the way a visitor in Korea does and returns structured JSON.

The actor uses Korean residential proxies (included in the price), retries failed requests, de-duplicates results and nests reviews and comments inside their parent row, so 20 places stay 20 rows even when each one carries 100 reviews. Your Python code only sends an input dict and iterates the dataset.

## Use cases

- **Korean local lead lists** — restaurants, clinics, beauty salons or academies with phone, road address, coordinates, booking link and rating.
- **Competitor research for F&B and retail** — menu prices, best-selling menu items with order share, hourly busyness per weekday and the review keywords customers vote for.
- **Naver Shopping price monitoring** — price, discount, stock, seller grade and delivery terms for any product keyword, sorted by sales, reviews or price.
- **Smart Store review mining** — buyer reviews with rating, option bought, photos and repurchase flag, lowest-rated first to find product defects.
- **PR and brand monitoring** — Naver News articles with full text, reporters and reader comments, filtered to the last hour, day or week.
- **Influencer and content research** — Naver Blog posts with full text, tags and images; every post of a single blog via `blogPosts`.
- **Korean SEO** — the full integrated results page (`serp`) for a keyword, block by block, plus autocomplete suggestions.
- **Real-estate analysis** — sale, jeonse and monthly rent listings for an apartment complex, with area, floor, direction and broker.
- **Trend tracking** — daily or weekly Shopping BEST charts and DataLab Shopping Insight keyword rankings by category, gender and age.

## Requirements

- Python **3.10+**
- A free [Apify account](https://console.apify.com/sign-up) — the free plan includes $5 of monthly credits
- **No** Naver account, Naver developer app, client secret or proxy subscription

## Quick start

```bash
git clone https://github.com/pro100chok/naver-map-shopping-blog-scraper-python.git
cd naver-map-shopping-blog-scraper-python
pip install -r requirements.txt
cp .env.example .env
# paste your APIFY_API_TOKEN into .env
python main.py
```

`main.py` runs a **Seoul cafe district scan** for `성수 카페`: it collects up to 40 places with full details and the newest reviews, ranks them by visitor reviews, aggregates the review keywords and best-selling menu items across the whole district, finds the most common busiest hour, cross-checks the names against recent Naver Blog posts, and writes `output.json` and `output.csv`.

The minimal call looks like this:

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")
run = client.actor("pro100chok/naver-all-in-one-scraper").call(run_input={
    "scrapeType": "places",
    "queries": ["강남역 맛집"],
    "maxItems": 20,
    "includeDetails": True,
})
for place in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(place["name"], place.get("rating"), place.get("phone"))
```

## How it works

1. **Pick a mode** with `scrapeType` — `places`, `shopping`, `blog`, `cafe`, `news`, `kin`, `serp`, `web`, `images`, `videos`, `autocomplete`, `shoppingBest`, `shoppingInsights`, `realEstate`, `webtoons`, `stocks`, `blogPosts` or `urls`.
2. **Fill `queries`** with Korean or English keywords, IDs (place ID, stock code `005930`, complex number, blog ID) or any Naver link. A pasted link is routed to the right parser automatically, so `smartstore.naver.com/.../products/...`, `n.news.naver.com/...`, `cafe.naver.com/...` and `naver.me/...` short links all work.
3. **Add depth only where you need it.** `includeDetails` opens each result for its full page (post text, menu, opening hours, popular times, seller company), `includeReviews` attaches place or product reviews, `includeComments` attaches cafe and news comments.
4. **Go past Naver Map's ~300-place limit** with `deepSearch`: the search area is split into smaller map squares until each one fits, then merged and de-duplicated. Combine it with `latitude`, `longitude` and `searchRadiusKm` to sweep a fixed area.
5. **Read the dataset** from Python, or export JSON, CSV or Excel from the Apify console.

## Example output

A Naver Map place with `includeDetails` (trimmed):

```json
{
  "type": "place",
  "query": "성수 카페",
  "id": "1251057335",
  "name": "비아트 성수",
  "category": "카페,디저트",
  "roadAddress": "서울 성동구 아차산로5길 24-45 2층",
  "phone": "0507-1482-5596",
  "latitude": 37.5471439,
  "longitude": 127.0542613,
  "rating": 4.83,
  "visitorReviewCount": 2653,
  "blogReviewCount": 1347,
  "popularMenus": [{ "name": "아메리카노(I)", "orderShare": 21 }],
  "popularTimes": [{ "day": "Monday", "busiestHour": 12, "hourly": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 39, 26, 19, 12, 14, 7, 19, 11, 5, 3, 0, 0, 0] }],
  "reviewKeywords": [{ "keyword": "디저트가 맛있어요", "count": 1784 }],
  "url": "https://map.naver.com/p/entry/place/1251057335"
}
```

A Naver Shopping product row carries `title`, `price`, `originalPrice`, `discountPercent`, `rating`, `reviewCount`, `stockQuantity`, `sellerName`, `sellerGrade`, `isBrandStore`, `deliveryFee`, `freeDelivery`, `categoryPath` and, with details, `brand`, `manufacturer`, `courier`, `sellerSalesCount` and `sellerStoreAge`. A real-estate listing carries `complexName`, `tradeType`, `price`, `deposit`, `monthlyRent`, `exclusiveAreaM2`, `floor`, `direction`, `brokerage` and `listedAt`.

## Input parameters

| Field | Type | What it does |
|---|---|---|
| `scrapeType` | enum | Naver service to scrape (default `places`) |
| `queries` | array | Keywords, IDs or Naver URLs; optional for `shoppingBest`, `shoppingInsights`, `webtoons` |
| `maxItems` | int | Max results per query (default 1,000) |
| `sortBy`, `period`, `dateFrom`, `dateTo` | enum / date | Order and date window for blog, cafe, news, Knowledge iN and media searches |
| `includeAds` | bool | Keep sponsored blog posts (flagged `isAd`) |
| `includeDetails` | bool | Open each result for its full data |
| `includeReviews`, `maxReviews`, `reviewSort` | bool / int / enum | Place and product reviews |
| `includeComments`, `maxComments` | bool / int | Cafe and news comments, Knowledge iN answers |
| `includePhotos`, `maxPhotos` | bool / int | Place photo URLs |
| `shoppingSort`, `minPrice`, `maxPrice` | enum / int | Product order (`REL`, `PURCHASE`, `REVIEW`, `LOW_PRICE`, `HIGH_PRICE`, `RECENT`) and price band in KRW |
| `bestRanking`, `bestPeriod`, `bestCategory` | enum | Shopping BEST chart type, period and category |
| `deepSearch`, `latitude`, `longitude`, `searchRadiusKm` | bool / string / int | Naver Map area sweep |
| `language` | enum | `ko` or `en` place names |
| `tradeTypes`, `realEstateSort` | array / enum | Real-estate deal types (`A1` sale, `B1` jeonse, `B2` monthly, `B3` short-term) and order |
| `insightCategory`, `timeUnit`, `startDate`, `endDate`, `device`, `gender`, `ages` | various | DataLab Shopping Insight filters |
| `webtoonDay`, `includeEpisodes`, `maxEpisodes` | enum / bool / int | Webtoon catalogue options |

## More examples

| File | What it shows |
|---|---|
| [`examples/01_basic_usage.py`](examples/01_basic_usage.py) | 20 Naver Map places for a keyword in a dozen lines |
| [`examples/02_shopping_price_tracker.py`](examples/02_shopping_price_tracker.py) | Best-selling Naver Shopping listings inside a KRW price band, with lowest-rated reviews |
| [`examples/03_news_brand_monitor.py`](examples/03_news_brand_monitor.py) | Last-24-hour Naver News coverage of a brand, top outlets and most-liked comments |
| [`examples/04_export_to_csv.py`](examples/04_export_to_csv.py) | Naver Blog posts for several keywords, organic only, to an Excel-friendly CSV |
| [`examples/05_export_to_google_sheets.py`](examples/05_export_to_google_sheets.py) | Daily Shopping BEST chart per category appended to a Google Sheet |

## How much does it cost?

The actor is pay-per-event, and proxies are included. Free-plan prices per 1,000 events: **$1.00** per search result (blog, cafe, news, BEST row, etc.), **$1.20** per Naver Map place, **$1.50** per shopping product or real-estate listing, **$2.50** per full-details page and **$0.50** per attached review or comment. Paid Apify plans pay less per event. A run of 1,000 blog posts costs about $1.

## FAQ

**Is there an official Naver API for this data?**
Naver's Open API returns short search snippets for registered apps with a daily quota. It does not return place reviews, menus, popular times, Smart Store seller data, news or cafe comments, or real-estate listings. The [Naver Scraper actor](https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) returns all of these without any keys.

**Do I need a Korean IP or a Naver account?**
No. Korean residential proxies are the default `proxyConfiguration` and are included in the price, and nothing requires a login.

**How do I get more than 300 places from Naver Map?**
Set `deepSearch` to `true`. The area is cut into smaller squares until each fits under Naver's cap, so a busy keyword returns every matching place in the area.

**Can I search in English?**
Yes, but Korean keywords give the richest results. Set `language` to `en` to get romanised or English place names where Naver has them.

**Can I scrape one specific Smart Store product or blog post?**
Yes. Paste the link into `queries` in any mode (or use `scrapeType: "urls"`) and the actor detects the link type.

**Why do some rows lack certain fields?**
Empty values are omitted rather than written as `null` — a place without a menu has no `menu` key. Use `.get()` in Python, as the examples do.

**Can I schedule daily monitoring?**
Yes. Save your input as an Apify task and attach a schedule, or run `examples/05_export_to_google_sheets.py` from cron.

## Related actors

- [Google Maps Scraper](https://apify.com/pro100chok/google-maps-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) — places, reviews, photos and emails outside Korea
- [RedNote Xiaohongshu Scraper](https://apify.com/pro100chok/rednote-xiaohongshu-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) — notes, creators, comments and transcripts from China's lifestyle platform
- [TikTok Shop Scraper](https://apify.com/pro100chok/tiktok-shop-scraper-usage?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) — products, sales and reviews
- [Amazon Scraper](https://apify.com/pro100chok/amazon-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) — products, reviews, sellers and best sellers
- [Yelp Scraper](https://apify.com/pro100chok/yelp-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) — local businesses, reviews and contacts

## License

MIT — see [LICENSE](LICENSE). This project is not affiliated with or endorsed by Naver Corporation. Collect only public data and handle personal data (reviewer nicknames, comments) in line with Korea's PIPA, GDPR and other rules that apply to you.

---

Built by [pro100chok](https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python) on Apify.
