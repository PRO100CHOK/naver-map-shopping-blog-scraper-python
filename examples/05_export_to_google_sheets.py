"""Daily Naver Shopping BEST chart appended to a Google Sheet.

Setup:
  1. Google Cloud console -> create a service account -> download its JSON key.
  2. Save it as service_account.json next to this file (it is gitignored).
  3. Share your spreadsheet with the service account's email address.
  4. Pick the BEST categories you follow in CATEGORIES.

Every run appends today's best-selling products for each category, so the sheet
turns into a ranking history you can chart. Schedule the script (or an Apify
task) once a day.

Actor: https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python
"""
import os
from datetime import datetime, timezone

import gspread
from apify_client import ApifyClient
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

SPREADSHEET = "Naver Shopping BEST history"
WORKSHEET = "daily"
CATEGORIES = {"50000002": "Beauty", "50000003": "Digital & appliances", "50000006": "Food"}
TOP_N = 30
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

load_dotenv()
client = ApifyClient(os.environ["APIFY_API_TOKEN"])
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

rows = []
for cat_id, cat_name in CATEGORIES.items():
    run = client.actor("pro100chok/naver-all-in-one-scraper").call(run_input={
        "scrapeType": "shoppingBest",
        "queries": [],
        "maxItems": TOP_N,
        "bestRanking": "PRODUCT_BUY",
        "bestPeriod": "DAILY",
        "bestCategory": cat_id,
    })
    for p in client.dataset(run["defaultDatasetId"]).iterate_items():
        rows.append([
            stamp, cat_name, p.get("rank"), p.get("title"), p.get("price"),
            p.get("discountPercent"), p.get("rating"), p.get("reviewCount"),
            p.get("sellerName"), p.get("rankingDate"), p.get("url"),
        ])
    print(f"{cat_name}: {TOP_N} ranked products")

header = ["collected", "category", "rank", "title", "price_krw", "discount_pct",
          "rating", "reviews", "seller", "ranking_date", "url"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
sheet = gspread.authorize(creds).open(SPREADSHEET)
try:
    ws = sheet.worksheet(WORKSHEET)
except gspread.WorksheetNotFound:
    ws = sheet.add_worksheet(WORKSHEET, rows=20000, cols=len(header))
    ws.append_row(header)

ws.append_rows(rows, value_input_option="USER_ENTERED")
print(f"Appended {len(rows)} rows to {SPREADSHEET}/{WORKSHEET}")
