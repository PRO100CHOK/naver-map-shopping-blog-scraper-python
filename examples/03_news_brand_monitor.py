"""Brand monitoring on Naver News — last 24 hours, full text and comments.

Collects every Naver News article about a brand published in the last day,
opens each one for the full text, attaches reader comments, and prints which
outlets wrote the most and which comments got the most likes.

Actor: https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python
"""
import os
from collections import Counter

from apify_client import ApifyClient
from dotenv import load_dotenv

BRAND = "현대자동차"

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/naver-all-in-one-scraper").call(run_input={
    "scrapeType": "news",
    "queries": [BRAND],
    "maxItems": 50,
    "sortBy": "date",
    "period": "1d",
    "includeDetails": True,
    "includeComments": True,
    "maxComments": 30,
})

articles = list(client.dataset(run["defaultDatasetId"]).iterate_items())
print(f"{len(articles)} articles about {BRAND} in the last 24 hours\n")

for press, n in Counter(a.get("press") or "-" for a in articles).most_common(8):
    print(f"  {n:>3}  {press}")

comments = [(c, a) for a in articles for c in (a.get("comments") or [])]
comments.sort(key=lambda ca: -(ca[0].get("likes") or 0))
print(f"\nMost-liked of {len(comments)} reader comments:")
for c, a in comments[:10]:
    print(f"  {c.get('likes') or 0:>5} likes  {(c.get('text') or '')[:80]}")
    print(f"           on: {(a.get('title') or '')[:70]}")
