.PHONY: all fetch serve install fetch-gtfs seed

PORT ?= 8000

all:
	$(MAKE) -j2 fetch serve

install:
	pip install -r requirements.txt

fetch:
	python worker/fetch_alerts.py

serve:
	@mkdir -p _site
	@CARTO_KEY=$$(grep ^CARTO_API_KEY .env | cut -d= -f2-); \
	sed 's|\.\./data/active_alerts\.geojson|data/active_alerts.geojson|g' web/index.html \
	  | sed "s|__CARTO_API_KEY__|$$CARTO_KEY|g" \
	  > _site/index.html
	@rm -rf _site/data && ln -s ../data _site/data
	python -m http.server $(PORT) --directory _site

seed:
	python worker/seed_data.py

fetch-gtfs:
	curl -fsSL https://metro.kingcounty.gov/GTFS/google_transit.zip -o /tmp/kc_gtfs.zip
	unzip -o /tmp/kc_gtfs.zip stops.txt -d data/
	rm /tmp/kc_gtfs.zip
