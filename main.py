"""Naver Map + Naver Blog scraper — Seoul cafe district market scan.

Use case: you are opening (or selling to) cafes in Seoul's Seongsu-dong and want
to know who already wins there. The script:

  1. pulls every Naver Map place for a keyword with full details and the newest
     visitor reviews (menu, popular menu items, popular times, review keywords),
  2. ranks the competitors by visitor review count and rating,
  3. counts which review keywords and best-selling menu items repeat across the
     whole district, and which hour of the day is the busiest,
  4. searches Naver Blog for the same keyword to see which places bloggers write
     about most,
  5. saves output.json (raw rows) and output.csv (one flat row per place).

Run:
    pip install -r requirements.txt
    cp .env.example .env
    python main.py

Actor: https://apify.com/pro100chok/naver-all-in-one-scraper?utm_source=github_pro100&utm_medium=readme&utm_campaign=naver-map-shopping-blog-scraper-python
"""
from __future__ import annotations

import csv
import json
import os
import sys
from collections import Counter
from pathlib import Path

from apify_client import ApifyClient
from apify_client.errors import ApifyApiError
from dotenv import load_dotenv

ACTOR_ID = "pro100chok/naver-all-in-one-scraper"
KEYWORD = "성수 카페"          # Korean keywords give the richest Naver results
MAX_PLACES = 40               # places to collect for the keyword
REVIEWS_PER_PLACE = 15        # newest visitor reviews attached to each place
BLOG_POSTS = 60               # Naver Blog posts to scan for place mentions

CSV_FIELDS = [
    "rank", "name", "category", "rating", "visitorReviewCount", "blogReviewCount",
    "phone", "roadAddress", "latitude", "longitude", "busiestHourMonday",
    "topMenu", "topReviewKeyword", "hasBooking", "blogMentions", "url",
]


def run_actor(client: ApifyClient, run_input: dict, label: str) -> list[dict]:
    """Start one actor run and return its dataset rows (empty list on failure)."""
    print(f"-> {label}")
    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input, timeout_secs=1800)
    except ApifyApiError as exc:
        print(f"   failed: {exc}")
        return []
    rows = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    print(f"   {len(rows)} rows")
    return rows


def busiest_hour(place: dict, day: str = "Monday") -> int | None:
    for entry in place.get("popularTimes") or []:
        if entry.get("day") == day:
            return entry.get("busiestHour")
    return None


def main() -> int:
    load_dotenv()
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("APIFY_API_TOKEN missing - copy .env.example to .env and paste your token.")
    client = ApifyClient(token)
    out = Path(__file__).parent

    # Step 1: competitors on Naver Map, with details and reviews
    places = run_actor(client, {
        "scrapeType": "places",
        "queries": [KEYWORD],
        "maxItems": MAX_PLACES,
        "includeDetails": True,
        "includeReviews": True,
        "maxReviews": REVIEWS_PER_PLACE,
        "reviewSort": "recent",
        "language": "ko",
    }, f"Naver Map places for {KEYWORD!r}")
    places = [p for p in places if p.get("type") == "place"]
    if not places:
        sys.exit("No places returned - try a broader keyword.")

    # Step 2: blog posts for the same keyword (search rows only, cheap)
    posts = run_actor(client, {
        "scrapeType": "blog",
        "queries": [KEYWORD],
        "maxItems": BLOG_POSTS,
        "sortBy": "date",
    }, f"Naver Blog posts for {KEYWORD!r}")
    blog_text = " ".join(
        f"{p.get('title') or ''} {p.get('description') or ''}" for p in posts
    )

    # Step 3: rank and aggregate
    places.sort(key=lambda p: (-(p.get("visitorReviewCount") or 0), -(p.get("rating") or 0)))
    keyword_votes: Counter[str] = Counter()
    menu_share: Counter[str] = Counter()
    hours: Counter[int] = Counter()
    rows = []
    for rank, p in enumerate(places, 1):
        for k in p.get("reviewKeywords") or []:
            keyword_votes[k.get("keyword")] += k.get("count") or 0
        menus = p.get("popularMenus") or []
        for m in menus:
            menu_share[m.get("name")] += 1
        hour = busiest_hour(p)
        if hour is not None:
            hours[hour] += 1
        kw = (p.get("reviewKeywords") or [{}])[0].get("keyword")
        rows.append({
            "rank": rank,
            "name": p.get("name"),
            "category": p.get("category"),
            "rating": p.get("rating"),
            "visitorReviewCount": p.get("visitorReviewCount"),
            "blogReviewCount": p.get("blogReviewCount"),
            "phone": p.get("phone"),
            "roadAddress": p.get("roadAddress"),
            "latitude": p.get("latitude"),
            "longitude": p.get("longitude"),
            "busiestHourMonday": hour,
            "topMenu": menus[0].get("name") if menus else None,
            "topReviewKeyword": kw,
            "hasBooking": p.get("hasBooking"),
            "blogMentions": blog_text.count(p.get("name") or "\0"),
            "url": p.get("url"),
        })

    # Step 4: report
    print(f"\nTop 10 of {len(rows)} places for {KEYWORD!r} by visitor reviews:")
    for r in rows[:10]:
        print(f"  {r['rank']:>2}. {str(r['rating'] or '-'):>4}  "
              f"{r['visitorReviewCount'] or 0:>6} reviews  "
              f"{r['blogMentions']:>2} blog hits  {r['name']}")

    print("\nWhat visitors praise most across the district:")
    for kw, votes in keyword_votes.most_common(8):
        print(f"  {votes:>7}  {kw}")

    print("\nMenu items that show up as best-sellers in several places:")
    for name, n in menu_share.most_common(8):
        print(f"  {n:>3} places  {name}")

    if hours:
        hour, n = hours.most_common(1)[0]
        print(f"\nMost common busiest hour on Mondays: {hour}:00 ({n} places)")

    low = [r for p, r in zip(places, rows) if (p.get("rating") or 5) < 4.3]
    print(f"\nPlaces rated under 4.3 (possible weak competitors): {len(low)}")

    # Step 5: save
    (out / "output.json").write_text(
        json.dumps({"places": places, "blogPosts": posts}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    with (out / "output.csv").open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved output.json and output.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
