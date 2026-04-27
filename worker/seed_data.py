#!/usr/bin/env python3
"""Write fake active_alerts.geojson for local UI testing (no API key needed)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

OUTPUT_FILE = Path("data/active_alerts.geojson")

_SEED_FEATURES = [
    {
        "stop_id": "1_29270",
        "stop_name": "3rd Ave & Pike St",
        "lat": 47.6097,
        "lon": -122.3375,
        "alert_type": "Stop Relocation",
        "status": "ongoing",
        "header": "Stop temporarily relocated due to construction",
        "description": (
            "Northbound stop at 3rd Ave & Pike St has moved one block north "
            "to 3rd Ave & Pine St (stop 1_29280) while sidewalk repairs are "
            "underway. Expected return: May 15."
        ),
        "url": "",
        "alert_id": "KCM-ALERT-001",
    },
    {
        "stop_id": "1_10914",
        "stop_name": "Aurora Ave N & N 65th St",
        "lat": 47.6753,
        "lon": -122.3467,
        "alert_type": "Route Change",
        "status": "ongoing",
        "header": "Route 5 detour — Aurora Ave N & 65th St",
        "description": (
            "Route 5 buses are detouring via Phinney Ave N due to a water main "
            "break on Aurora Ave N between N 63rd and N 67th. Stop 1_10914 is "
            "temporarily not served. Use nearby stop 1_10920 on Phinney Ave N."
        ),
        "url": "https://kingcounty.gov/en/dept/metro/rider-tools/alerts",
        "alert_id": "KCM-ALERT-002",
    },
    {
        "stop_id": "1_75403",
        "stop_name": "Bellevue Transit Center Bay A",
        "lat": 47.6154,
        "lon": -122.2007,
        "alert_type": "Stop Closure",
        "status": "ongoing",
        "header": "Bellevue TC Bay A temporarily closed",
        "description": (
            "Bay A at Bellevue Transit Center is closed for light rail "
            "construction staging. Routes 221, 226, 240 boarding from "
            "temporary Bay A-1 on NE 6th St."
        ),
        "url": "",
        "alert_id": "KCM-ALERT-003",
    },
    {
        "stop_id": "1_55699",
        "stop_name": "Rainier Ave S & S Alaska St",
        "lat": 47.5612,
        "lon": -122.2896,
        "alert_type": "Route Change",
        "status": "upcoming",
        "header": "Routes 7, 9 detour — Columbia City",
        "description": (
            "Routes 7 and 9 are detouring around a utility emergency on "
            "Rainier Ave S between S Alaska St and S Edmunds St. "
            "Expect 5–10 minute delays."
        ),
        "url": "",
        "alert_id": "KCM-ALERT-004",
    },
    {
        "stop_id": "1_38486",
        "stop_name": "15th Ave NE & NE Campus Pkwy",
        "lat": 47.6584,
        "lon": -122.3126,
        "alert_type": "Stop Relocation",
        "status": "ongoing",
        "header": "UW area stop relocated for bridge work",
        "description": (
            "Stop 1_38486 (15th Ave NE & NE Campus Pkwy) is temporarily "
            "relocated 150 ft south to in front of the UW Tower entrance. "
            "Serving routes 65, 67, 372."
        ),
        "url": "https://kingcounty.gov/en/dept/metro/rider-tools/alerts",
        "alert_id": "KCM-ALERT-005",
    },
    {
        "stop_id": "1_46980",
        "stop_name": "Renton Transit Center Bay 1",
        "lat": 47.4796,
        "lon": -122.2171,
        "alert_type": "Route Change",
        "status": "ongoing",
        "header": "Renton TC — Bay 1 inaccessible",
        "description": (
            "Renton Transit Center Bay 1 is blocked by a broken-down vehicle. "
            "Routes 101, 102, 143 are loading from the S 3rd St curb stop "
            "while the bay is cleared. Estimated clearance: 2 hours."
        ),
        "url": "",
        "alert_id": "KCM-ALERT-006",
    },
]


def main() -> None:
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [s["lon"], s["lat"]],
            },
            "properties": {
                "alert_id": s["alert_id"],
                "stop_id": s["stop_id"],
                "stop_name": s["stop_name"],
                "alert_type": s["alert_type"],
                "status": s["status"],
                "header": s["header"],
                "description": s["description"],
                "url": s["url"],
            },
        }
        for s in _SEED_FEATURES
    ]

    geojson = {
        "type": "FeatureCollection",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "features": features,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT_FILE.with_suffix(".geojson.tmp")
    tmp.write_text(json.dumps(geojson, indent=2), encoding="utf-8")
    os.replace(tmp, OUTPUT_FILE)
    print(f"Wrote {len(features)} seed features → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
