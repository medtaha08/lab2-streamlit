"""
Lab 1 - Google Play Store API Scraper
Mental Health & Wellness AI Applications
"""

import json
import time
from datetime import datetime
from google_play_scraper import search, app, reviews, Sort


# ─────────────────────────────────────────────
# 1. SEARCH QUERIES
# ─────────────────────────────────────────────
SEARCH_QUERIES = [
    "mental health AI",
    "AI therapy chatbot",
    "anxiety depression app",
    "wellness meditation AI",
    "mental wellness tracker",
    "AI mood tracker",
    "mindfulness AI assistant",
]

LANG = "en"
COUNTRY = "us"
N_RESULTS_PER_QUERY = 20     # apps per search query
N_REVIEWS_PER_APP = 100      # reviews per app (increase if you want more)


# ─────────────────────────────────────────────
# 2. COLLECT APP IDs (deduplicated)
# ─────────────────────────────────────────────
def collect_app_ids(queries):
    app_ids = set()
    print(f"\n{'='*50}")
    print("STEP 1: Searching for apps...")
    print(f"{'='*50}")

    for query in queries:
        print(f"  🔍 Query: '{query}'")
        try:
            results = search(
                query,
                lang=LANG,
                country=COUNTRY,
                n_hits=N_RESULTS_PER_QUERY,
            )
            for r in results:
                app_ids.add(r["appId"])
            print(f"     ✅ Found {len(results)} apps (total unique: {len(app_ids)})")
        except Exception as e:
            print(f"     ❌ Error: {e}")
        time.sleep(1)  # be polite to the API

    return list(app_ids)


# ─────────────────────────────────────────────
# 3. EXTRACT APP DETAILS
# ─────────────────────────────────────────────
def extract_app_details(app_ids):
    apps_data = []
    print(f"\n{'='*50}")
    print(f"STEP 2: Extracting details for {len(app_ids)} apps...")
    print(f"{'='*50}")

    for i, app_id in enumerate(app_ids, 1):
        print(f"  [{i}/{len(app_ids)}] {app_id}")
        try:
            details = app(app_id, lang=LANG, country=COUNTRY)

            # Keep only the most useful fields
            apps_data.append({
                "appId":            details.get("appId"),
                "title":            details.get("title"),
                "developer":        details.get("developer"),
                "developerId":      details.get("developerId"),
                "developerEmail":   details.get("developerEmail"),
                "developerWebsite": details.get("developerWebsite"),
                "genre":            details.get("genre"),
                "genreId":          details.get("genreId"),
                "description":      details.get("description"),
                "summary":          details.get("summary"),
                "score":            details.get("score"),
                "ratings":          details.get("ratings"),
                "reviews_count":    details.get("reviews"),
                "installs":         details.get("installs"),
                "minInstalls":      details.get("minInstalls"),
                "maxInstalls":      details.get("maxInstalls"),
                "free":             details.get("free"),
                "price":            details.get("price"),
                "currency":         details.get("currency"),
                "inAppPurchases":   details.get("inAppPurchases"),
                "containsAds":      details.get("containsAds"),
                "androidVersion":   details.get("androidVersion"),
                "contentRating":    details.get("contentRating"),
                "released":         details.get("released"),
                "updated":          details.get("updated"),
                "version":          details.get("version"),
                "url":              details.get("url"),
                "icon":             details.get("icon"),
                "screenshots":      details.get("screenshots"),
                "headerImage":      details.get("headerImage"),
                "video":            details.get("video"),
                "recentChanges":    details.get("recentChanges"),
                "histogram":        details.get("histogram"),   # rating breakdown 1-5★
                "scraped_at":       datetime.utcnow().isoformat(),
            })
            print(f"     ✅ '{details.get('title')}' | ⭐ {details.get('score')} | 📥 {details.get('installs')}")
        except Exception as e:
            print(f"     ❌ Error: {e}")

        time.sleep(0.5)

    return apps_data


# ─────────────────────────────────────────────
# 4. EXTRACT REVIEWS
# ─────────────────────────────────────────────
def extract_reviews(app_ids):
    all_reviews = {}
    print(f"\n{'='*50}")
    print(f"STEP 3: Extracting reviews ({N_REVIEWS_PER_APP} per app)...")
    print(f"{'='*50}")

    for i, app_id in enumerate(app_ids, 1):
        print(f"  [{i}/{len(app_ids)}] {app_id}")
        try:
            result, _ = reviews(
                app_id,
                lang=LANG,
                country=COUNTRY,
                sort=Sort.MOST_RELEVANT,
                count=N_REVIEWS_PER_APP,
            )

            cleaned = []
            for r in result:
                cleaned.append({
                    "reviewId":       r.get("reviewId"),
                    "userName":       r.get("userName"),
                    "userImage":      r.get("userImage"),
                    "content":        r.get("content"),
                    "score":          r.get("score"),        # 1-5 stars
                    "thumbsUpCount":  r.get("thumbsUpCount"),
                    "reviewCreatedVersion": r.get("reviewCreatedVersion"),
                    "at":             r.get("at").isoformat() if r.get("at") else None,
                    "replyContent":   r.get("replyContent"),
                    "repliedAt":      r.get("repliedAt").isoformat() if r.get("repliedAt") else None,
                    "appVersion":     r.get("appVersion"),
                })

            all_reviews[app_id] = cleaned
            print(f"     ✅ {len(cleaned)} reviews collected")

        except Exception as e:
            print(f"     ❌ Error: {e}")
            all_reviews[app_id] = []

        time.sleep(0.5)

    return all_reviews


# ─────────────────────────────────────────────
# 5. SAVE TO JSON
# ─────────────────────────────────────────────
def save_to_json(apps_data, all_reviews, output_file="mental_health_apps.json"):
    output = {
        "metadata": {
            "scraped_at":     datetime.utcnow().isoformat(),
            "total_apps":     len(apps_data),
            "total_reviews":  sum(len(v) for v in all_reviews.values()),
            "search_queries": SEARCH_QUERIES,
            "language":       LANG,
            "country":        COUNTRY,
        },
        "apps":    apps_data,
        "reviews": all_reviews,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    size_mb = round(__import__("os").path.getsize(output_file) / 1024 / 1024, 2)
    print(f"\n{'='*50}")
    print(f"✅ Data saved to '{output_file}'")
    print(f"   📱 Apps:    {output['metadata']['total_apps']}")
    print(f"   💬 Reviews: {output['metadata']['total_reviews']}")
    print(f"   💾 Size:    {size_mb} MB")
    print(f"{'='*50}\n")


# ─────────────────────────────────────────────
# 6. MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 Lab 1 - Google Play Scraper")
    print(f"   Queries : {len(SEARCH_QUERIES)}")
    print(f"   Apps/query : {N_RESULTS_PER_QUERY}")
    print(f"   Reviews/app: {N_REVIEWS_PER_APP}")

    # Step 1 — collect unique app IDs
    app_ids = collect_app_ids(SEARCH_QUERIES)

    # Step 2 — get full details for each app
    apps_data = extract_app_details(app_ids)

    # Step 3 — get reviews
    all_reviews = extract_reviews(app_ids)

    # Step 4 — save everything
    save_to_json(apps_data, all_reviews)