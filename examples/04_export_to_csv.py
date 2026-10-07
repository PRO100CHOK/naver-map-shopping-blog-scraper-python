"""Naver Blog posts for several keywords -> filtered CSV with pandas.

Searches Naver Blog for each keyword, drops sponsored posts, keeps posts from
the last month, and writes a CSV you can open in Excel (UTF-8 with BOM so the
Korean text shows correctly).

Actor: https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python
"""
import os

import pandas as pd
from apify_client import ApifyClient
from dotenv import load_dotenv

KEYWORDS = ["제주 카페 추천", "부산 호텔 후기", "서울 데이트 코스"]

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])

run = client.actor("pro100chok/naver-all-in-one-scraper").call(run_input={
    "scrapeType": "blog",
    "queries": KEYWORDS,
    "maxItems": 100,
    "sortBy": "date",
    "period": "1m",
    "includeAds": False,
})

df = pd.DataFrame(client.dataset(run["defaultDatasetId"]).iterate_items())
if df.empty:
    raise SystemExit("No posts returned.")

if "isAd" in df.columns:  # keep organic posts only
    df = df[df["isAd"].fillna(False).astype(bool) == False]  # noqa: E712
cols = [c for c in ["query", "publishedAt", "title", "blogName", "blogId",
                    "imageCount", "url", "description"] if c in df.columns]
df = df[cols].sort_values(["query", "publishedAt"], ascending=[True, False])

print(df.groupby("query").size().rename("posts").to_string())
print("\nMost active bloggers:")
print(df["blogName"].value_counts().head(10).to_string())

df.to_csv("output.csv", index=False, encoding="utf-8-sig")
print(f"\nSaved {len(df)} rows to output.csv")
