.PHONY: all fetch serve install fetch-gtfs seed

all:
	$(MAKE) -j2 fetch serve

install:
	pip install -r requirements.txt

fetch:
	python worker/fetch_alerts.py

serve:
	python -m http.server 8000

seed:
	python worker/seed_data.py

fetch-gtfs:
	curl -fsSL https://metro.kingcounty.gov/GTFS/google_transit.zip -o /tmp/kc_gtfs.zip
	unzip -o /tmp/kc_gtfs.zip stops.txt -d data/
	rm /tmp/kc_gtfs.zip
