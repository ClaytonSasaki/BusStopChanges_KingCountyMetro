#!/usr/bin/env python3
"""Poll GTFS-RT service alerts, classify by header text, write GeoJSON."""

import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2

load_dotenv()

OBA_API_KEY: str = os.environ.get("OBA_API_KEY", "")
ALERTS_URL = (
    "https://api.pugetsound.onebusaway.org/api/gtfs_realtime/"
    "alerts-for-agency/1.pb"
)
STOPS_FILE = Path("data/stops.txt")
OUTPUT_FILE = Path("data/active_alerts.geojson")
POLL_INTERVAL = 600  # seconds

# KC Metro sends everything as UNKNOWN_EFFECT; filter by these effect values.
_RELEVANT_EFFECTS = {
    gtfs_realtime_pb2.Alert.STOP_MOVED,
    gtfs_realtime_pb2.Alert.DETOUR,
    gtfs_realtime_pb2.Alert.UNKNOWN_EFFECT,
}


def load_stops() -> dict[str, dict]:
    if not STOPS_FILE.exists():
        print(
            f"ERROR: {STOPS_FILE} not found. "
            "Run 'make fetch-gtfs' to download the static GTFS.",
            file=sys.stderr,
        )
        sys.exit(1)
    stops: dict[str, dict] = {}
    with STOPS_FILE.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            stops[row["stop_id"]] = {
                "stop_name": row["stop_name"],
                "stop_lat": float(row["stop_lat"]),
                "stop_lon": float(row["stop_lon"]),
            }
    return stops


def _classify_alert(header: str) -> str:
    """Derive alert type from header text (effect enum is not reliable for KC Metro)."""
    h = header.lower()
    if "relocated" in h or "relocation" in h:
        return "Stop Relocation"
    if "closed" in h or "closure" in h:
        return "Stop Closure"
    return "Route Change"


def _get_status(alert: gtfs_realtime_pb2.Alert, now: int) -> str | None:
    """Return 'ongoing', 'upcoming', or None if all periods are past."""
    if not alert.active_period:
        return "ongoing"
    for p in alert.active_period:
        start = p.start or 0
        end = p.end or float("inf")
        if start <= now <= end:
            return "ongoing"
    for p in alert.active_period:
        if (p.start or 0) > now:
            return "upcoming"
    return None  # all periods expired


def _translation(field) -> str:
    for tr in field.translation:
        if tr.language in ("en", "en-US", ""):
            return tr.text
    if field.translation:
        return field.translation[0].text
    return ""


def fetch_and_write(stops: dict[str, dict]) -> None:
    params: dict[str, str] = {}
    if OBA_API_KEY:
        params["key"] = OBA_API_KEY

    resp = httpx.get(ALERTS_URL, params=params, timeout=30)
    resp.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)

    now = int(datetime.now(timezone.utc).timestamp())
    features: list[dict] = []

    for entity in feed.entity:
        if not entity.HasField("alert"):
            continue
        alert = entity.alert
        if alert.effect not in _RELEVANT_EFFECTS:
            continue

        status = _get_status(alert, now)
        if status is None:
            continue  # expired

        header = _translation(alert.header_text)
        alert_type = _classify_alert(header)
        description = _translation(alert.description_text)
        url = _translation(alert.url)

        for informed in alert.informed_entity:
            stop_id = informed.stop_id
            if not stop_id or stop_id not in stops:
                continue
            stop = stops[stop_id]
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [stop["stop_lon"], stop["stop_lat"]],
                    },
                    "properties": {
                        "alert_id": entity.id,
                        "stop_id": stop_id,
                        "stop_name": stop["stop_name"],
                        "alert_type": alert_type,
                        "status": status,
                        "header": header,
                        "description": description,
                        "url": url,
                    },
                }
            )

    geojson = {
        "type": "FeatureCollection",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "features": features,
    }

    tmp = OUTPUT_FILE.with_suffix(".geojson.tmp")
    tmp.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    os.replace(tmp, OUTPUT_FILE)

    by_type: dict[str, int] = {}
    for f in features:
        t = f["properties"]["alert_type"]
        by_type[t] = by_type.get(t, 0) + 1
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {len(features)} feature(s): {by_type} → {OUTPUT_FILE}")


def main(once: bool = False) -> None:
    if not OBA_API_KEY:
        print("WARNING: OBA_API_KEY not set; requests may be rate-limited or rejected.")

    stops = load_stops()
    print(f"Loaded {len(stops)} stops from {STOPS_FILE}")

    while True:
        try:
            fetch_and_write(stops)
        except httpx.HTTPStatusError as exc:
            print(f"HTTP error: {exc.response.status_code} {exc.request.url}")
        except Exception as exc:  # noqa: BLE001
            print(f"Error: {exc}")
        if once:
            break
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Fetch once and exit")
    main(once=parser.parse_args().once)
