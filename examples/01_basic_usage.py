"""20 Naver Map places for one keyword — name, rating, phone, address.

`queries` accepts Korean or English keywords, place IDs or Naver Map links.

Actor: https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python
"""
import os

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/naver-all-in-one-scraper").call(run_input={
    "scrapeType": "places",
    "queries": ["강남역 맛집"],
    "maxItems": 20,
})

for p in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"{str(p.get('rating') or '-'):>4}  {p.get('visitorReviewCount') or 0:>6} reviews  "
          f"{p.get('name')}  |  {p.get('phone') or '-'}  |  {p.get('roadAddress') or p.get('address')}")
