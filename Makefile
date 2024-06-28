INTER := intermediate
ENV := env

$(ENV):
	mamba create -p $(ENV) -y -c conda-forge pygeoprocessing voila jupyter wget ipyleaflet

$(INTER):
	mkdir intermediate

$(INTER)/Base_Data.zip: $(INTER) $(ENV)
	$(ENV)/bin/wget -O $(INTER)/Base_Data.zip --no-use-server-timestamps https://storage.googleapis.com/releases.naturalcapitalproject.org/invest/3.13.0/data/Base_Data.zip

$(INTER)/global_dem.tif: $(INTER)/Base_Data.zip
	unzip -p $(INTER)/Base_Data.zip Base_Data/global_dem.tif > $(INTER)/global_dem.tif

$(INTER)/rescaled.tif: $(INTER)/global_dem.tif
	$(ENV)/bin/python rescale.py $(INTER)/global_dem.tif $(INTER)/rescaled.tif stats.json

$(INTER)/elevation.tif: $(INTER)/rescaled.tif
	$(ENV)/bin/gdaldem color-relief -co COMPRESS=LZW $(INTER)/rescaled.tif elevation-color-profile-grass.txt $(INTER)/elevation.tif

tiles: $(INTER)/elevation.tif
	$(ENV)/bin/gdal2tiles.py --xyz -r near --zoom=1-7 --processes=5 $(INTER)/elevation.tif tiles

serve-jupyter: tiles
	jupyter notebook demo.ipynb

serve-voila: tiles
	voila demo.ipynb

.PHONY: restart-vm
restart-vm:
	gcloud compute instances reset --zone=us-west1-b --project=sdss-natcap-gef-ckan voila-apps
