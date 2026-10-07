"""Naver Shopping price check — best-selling listings inside a price band.

Pulls the best-selling Naver Shopping / Smart Store listings for a product
keyword, keeps only the ones between MIN and MAX price (KRW), and prints the
cheapest sellers with delivery terms. Add buyer reviews with includeReviews.

Actor: https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python
"""
import os

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError
from dotenv import load_dotenv

KEYWORD = "에어팟 프로"
MIN_PRICE, MAX_PRICE = 200000, 400000

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

try:
    run = client.actor("pro100chok/naver-all-in-one-scraper").call(run_input={
        "scrapeType": "shopping",
        "queries": [KEYWORD],
        "maxItems": 60,
        "shoppingSort": "PURCHASE",
        "minPrice": MIN_PRICE,
        "maxPrice": MAX_PRICE,
        "includeReviews": True,
        "maxReviews": 5,
        "reviewSort": "ratingLow",
    })
except ApifyApiError as exc:
    raise SystemExit(f"Run failed: {exc}")

products = list(client.dataset(run["defaultDatasetId"]).iterate_items())
products.sort(key=lambda p: p.get("price") or 0)

print(f"{len(products)} listings for {KEYWORD!r} between {MIN_PRICE:,} and {MAX_PRICE:,} KRW\n")
for p in products[:15]:
    ship = "free" if p.get("freeDelivery") else f"{p.get('deliveryFee') or '?'} KRW"
    print(f"{p.get('price') or 0:>9,} KRW  -{p.get('discountPercent') or 0:>2}%  "
          f"{str(p.get('rating') or '-'):>4} ({p.get('reviewCount') or 0} reviews)  "
          f"ship {ship:<10} {p.get('sellerName')}")
    for r in (p.get("reviews") or [])[:2]:
        print(f"      [{r.get('rating')}] {(r.get('text') or '')[:90]}")
