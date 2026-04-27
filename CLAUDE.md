# KC Metro Temporary Stop Tracker

Tracks temporarily relocated King County Metro bus stops by parsing
the GTFS-Realtime service alerts feed and joining against static GTFS.

## Architecture
- `worker/` — Python script, polls GTFS-RT alerts every 10 min, emits GeoJSON
- `web/` — static frontend, Leaflet map, reads the GeoJSON
- `data/` — static GTFS stops + latest GeoJSON output (both tracked in git)
- `.github/workflows/refresh.yml` — GitHub Actions cron keeps GeoJSON current on Pages

## Conventions
- Python 3.11+, type hints, ruff for linting
- Use `gtfs-realtime-bindings` for protobuf parsing
- Keep secrets (OBA API key) in .env, never commit

## GTFS-RT feed URL
```
https://api.pugetsound.onebusaway.org/api/gtfs_realtime/alerts-for-agency/1.pb?key={OBA_API_KEY}
```
Agency ID `1` = King County Metro.

## Alert classification
KC Metro sends all alerts with `effect=UNKNOWN_EFFECT` — the effect enum is not
useful. Alert type is derived from the `header_text` field by keyword matching:

| Keyword in header | `alert_type` |
|-------------------|--------------|
| "relocated" / "relocation" | `Stop Relocation` |
| "closed" / "closure" | `Stop Closure` |
| anything else | `Route Change` |

## GeoJSON feature schema (`data/active_alerts.geojson`)
Each `Feature` in the `FeatureCollection` carries:

| Property | Type | Description |
|----------|------|-------------|
| `alert_id` | string | GTFS-RT entity ID |
| `stop_id` | string | GTFS stop ID (plain integer string, matches stops.txt) |
| `stop_name` | string | Human-readable stop name from stops.txt |
| `alert_type` | string | `Stop Closure`, `Stop Relocation`, or `Route Change` |
| `status` | string | `ongoing` or `upcoming` |
| `header` | string | Short alert headline |
| `description` | string | Full alert body text |
| `url` | string | Link to more info (may be empty) |

Top-level field `generated_at` is an ISO-8601 UTC timestamp of the last fetch.

## Atomic write pattern
`fetch_alerts.py` writes to `data/active_alerts.geojson.tmp` then calls
`os.replace()` so the web server never serves a partial file.

## Worker flags
- No flags: infinite poll loop every 10 minutes (local use via `make fetch`)
- `--once`: single fetch then exit (used by GitHub Actions)
