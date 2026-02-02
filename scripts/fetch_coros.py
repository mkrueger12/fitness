#!/usr/bin/env python3
"""
Fetch all activity data from Coros Training Hub (t.coros.com).

Uses the undocumented Coros team API at teamapi.coros.com/activity/query
to retrieve detailed activity metrics not visible in the web UI table.

Authentication:
    Requires a valid access token from the CPL-coros-token cookie.
    To get a fresh token:
    1. Log into https://t.coros.com in Chrome
    2. Open DevTools > Application > Cookies
    3. Copy the value of CPL-coros-token
    4. Update the TOKEN constant below

Output:
    - /tmp/coros_raw.json: Raw API response data
    - /tmp/coros_activities_api.csv: Processed CSV with columns:
        date, name, type, distance_mi, duration, pace, avg_hr, cadence,
        ascent_ft, descent_ft, calories, training_load, steps, sets, device

Activity types (mode codes):
    8=Run, 9=Bike, 10=Swim, 15=Trail Run, 16=Hike, 18=GPS Cardio,
    20=Track Run, 23=Strength, 31=Walk, 98=Skimo

Usage:
    python scripts/fetch_coros.py
    cp /tmp/coros_activities_api.csv data/coros_activities.csv
"""

import requests
import json
import csv
from datetime import datetime

TOKEN = "2MY7F83LYBBW6QZJLS3Z8ZWN96QM8BCU"
API_URL = "https://teamapi.coros.com/activity/query"

def fetch_all_activities():
    """Fetch all activities from the API"""
    all_activities = []
    page = 1

    while True:
        print(f"Fetching page {page}...", end=" ", flush=True)
        resp = requests.get(
            API_URL,
            params={"size": 100, "pageNumber": page, "modeList": ""},
            headers={"accesstoken": TOKEN}
        )
        data = resp.json()

        if data.get("result") == "1031":
            print(f"Error: {data.get('message')}")
            break

        activities = data.get("data", {}).get("dataList", [])
        if not activities:
            print("No more data")
            break

        all_activities.extend(activities)
        total = data.get("data", {}).get("count", 0)
        print(f"Got {len(activities)} activities (total: {len(all_activities)}/{total})")

        if len(all_activities) >= total:
            break

        page += 1

    return all_activities

def format_time(seconds):
    """Format seconds as HH:MM:SS"""
    if not seconds:
        return ""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def format_pace(avg_speed):
    """Convert speed (sec/km) to pace (min'sec"/mi)"""
    if not avg_speed:
        return ""
    # avg_speed is in seconds per km
    sec_per_mile = avg_speed * 1.60934
    minutes = int(sec_per_mile // 60)
    seconds = int(sec_per_mile % 60)
    return f"{minutes}'{seconds:02d}\"/mi"

def meters_to_miles(meters):
    """Convert meters to miles"""
    if not meters:
        return ""
    return round(meters / 1609.344, 2)

def format_date(date_int):
    """Convert date int (YYYYMMDD) to ISO format"""
    s = str(date_int)
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"

MODE_NAMES = {
    8: "Run",
    9: "Bike",  # Mountain Bike from data
    10: "Swim",
    15: "Trail Run",
    16: "Hike",
    18: "GPS Cardio",
    20: "Track Run",
    23: "Strength",
    31: "Walk",
    98: "Skimo",
}

def main():
    activities = fetch_all_activities()
    print(f"\nTotal activities fetched: {len(activities)}")

    # Save raw JSON
    with open("/tmp/coros_raw.json", "w") as f:
        json.dump(activities, f, indent=2)
    print("Saved raw JSON to /tmp/coros_raw.json")

    # Convert to CSV
    rows = []
    for a in activities:
        date = format_date(a.get("date", 0))
        name = a.get("name", "")
        mode = a.get("mode", 0)
        mode_name = MODE_NAMES.get(mode, f"Mode {mode}")

        # Basic metrics
        distance_m = a.get("distance", 0)
        distance_mi = meters_to_miles(distance_m) if distance_m else ""
        duration_sec = a.get("totalTime", 0) or a.get("workoutTime", 0)
        duration = format_time(duration_sec)

        # Cardio metrics
        avg_hr = a.get("avgHr", 0) or ""
        avg_speed = a.get("avgSpeed", 0)
        pace = format_pace(avg_speed) if avg_speed else ""
        cadence = a.get("avgCadence", 0) or ""

        # Elevation
        ascent_m = a.get("ascent", 0)
        ascent_ft = round(ascent_m * 3.28084) if ascent_m else ""
        descent_m = a.get("descent", 0)
        descent_ft = round(descent_m * 3.28084) if descent_m else ""

        # Other
        calories = a.get("calorie", 0)
        if calories:
            calories = round(calories / 1000)  # Convert from joules-ish to kcal
        else:
            calories = ""

        training_load = a.get("trainingLoad", 0) or ""
        steps = a.get("step", 0) or ""
        sets = a.get("sets", 0) or ""
        device = a.get("device", "")

        rows.append({
            "date": date,
            "name": name,
            "type": mode_name,
            "distance_mi": distance_mi,
            "duration": duration,
            "pace": pace,
            "avg_hr": avg_hr,
            "cadence": cadence,
            "ascent_ft": ascent_ft,
            "descent_ft": descent_ft,
            "calories": calories,
            "training_load": training_load,
            "steps": steps,
            "sets": sets,
            "device": device,
        })

    # Write CSV
    fieldnames = ["date", "name", "type", "distance_mi", "duration", "pace",
                  "avg_hr", "cadence", "ascent_ft", "descent_ft", "calories",
                  "training_load", "steps", "sets", "device"]

    with open("/tmp/coros_activities_api.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved CSV to /tmp/coros_activities_api.csv")

    # Summary stats
    cardio = [r for r in rows if r["type"] in ["Run", "Trail Run", "Track Run", "Bike", "Hike", "Walk", "Swim", "GPS Cardio", "Skimo"]]
    strength = [r for r in rows if r["type"] == "Strength"]

    print(f"\nSummary:")
    print(f"  Total activities: {len(rows)}")
    print(f"  Cardio activities: {len(cardio)}")
    print(f"  Strength sessions: {len(strength)}")

    # Total distance and elevation for cardio
    total_dist = sum(float(r["distance_mi"]) for r in cardio if r["distance_mi"])
    total_ascent = sum(int(r["ascent_ft"]) for r in cardio if r["ascent_ft"])
    print(f"  Total cardio distance: {total_dist:.1f} miles")
    print(f"  Total elevation gain: {total_ascent:,} ft")

if __name__ == "__main__":
    main()
