# KC Metro Temporary Stop Tracker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

Polls King County Metro's GTFS-Realtime service alerts feed every 10 minutes,
classifies alerts as **Stop Closure**, **Stop Relocation**, or **Route Change**,
and displays affected stops on an interactive Leaflet map — including upcoming
changes as well as ongoing ones.

## Live map

When hosted on GitHub Pages the map is updated automatically by a GitHub Actions
workflow every 10 minutes.

## Prerequisites

- Python 3.11+
- An [OneBusAway API key](https://onebusaway.org/api-key-request/) for the
  Puget Sound region (`api.pugetsound.onebusaway.org`)

## Local setup

```bash
# 1. Copy and fill in your API key
cp .env.example .env
#    → edit .env and set OBA_API_KEY=<your key>

# 2. Install Python dependencies
make install

# 3. Download King County Metro static GTFS (extracts stops.txt into data/)
make fetch-gtfs
```

> If `make fetch-gtfs` fails due to a URL change, download the GTFS zip
> manually from https://www.soundtransit.org/help-contacts/business-information/open-transit-data-otd/otd-downloads
> and run `unzip google_transit.zip stops.txt -d data/`.

## Running locally

```bash
# Start both the poller and the local web server in parallel
make all

# Or in two separate terminals:
make fetch   # polls every 10 min, writes data/active_alerts.geojson
make serve   # serves project root at http://localhost:8000
```

Open **http://localhost:8000/web/** in a browser.

**Testing without an API key:** `make seed` writes realistic fake data so you
can develop against the map UI before your key arrives.

## Architecture

See `CLAUDE.md` for full conventions and field-level schema documentation.

| Path | Role |
|------|------|
| `worker/fetch_alerts.py` | GTFS-RT poller — classifies alerts, writes `data/active_alerts.geojson` |
| `worker/seed_data.py` | Writes fake GeoJSON for UI testing (`make seed`) |
| `web/index.html` | Leaflet SPA — reads the GeoJSON, auto-refreshes every 10 min |
| `data/stops.txt` | Static GTFS stops (downloaded by `make fetch-gtfs`) |
| `data/active_alerts.geojson` | Latest alert output — committed and served via Pages |
| `.github/workflows/refresh.yml` | Scheduled Actions workflow — keeps GeoJSON up to date |

## License

[MIT](LICENSE.txt) © 2026 Clayton Sasaki
