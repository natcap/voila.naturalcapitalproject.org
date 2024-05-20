import json

import branca
import interactive_options
import ipyleaflet
import ipywidgets
import matplotlib
import requests
import shapely.geometry
from osgeo import gdal

gdal.DontUseExceptions()

DATASETS_BASE_URL = "https://storage.googleapis.com/natcap-data-cache/global"
DATASETS_DIRECTORY_URL = f"{DATASETS_BASE_URL}/directory.json"
DATASET_DIRECTORY = requests.get(
    DATASETS_DIRECTORY_URL).json()['public_layers']


def get_url(dataset_key):
    return (
        f"{DATASETS_BASE_URL}/{dataset_key}/"
        f"{DATASET_DIRECTORY[dataset_key]['download']}")


def _dataset_colors_html(dataset_key):
    assert dataset_key in DATASET_DIRECTORY, (
        f"Unknown dataset key {dataset_key}")
    dataset_info = DATASET_DIRECTORY[dataset_key]
    colors_filename = dataset_info['colors']
    minimum = dataset_info['data']['min']
    maximum = dataset_info['data']['max']

    colors_url = f"{DATASETS_BASE_URL}/{dataset_key}/{colors_filename}"

    colormap_list = []
    for line in requests.get(colors_url).iter_lines():
        # Requires that we have ASCII text only.
        # GRASS color files allow ":" as a color separator, so replace with
        # space for ease of parsing.
        line = line.decode('ASCII').replace(':', ' ')
        if line.startswith('#'):
            continue
        percent, colors = line.split(' ', 1)  # Stop after the first split

        colors = [c for c in colors.split(' ') if c]
        try:
            if len(colors) == 1:
                r, g, b = matplotlib.colors.to_rgb(colors[0])
            elif len(colors) == 3:
                r, g, b = colors
            else:
                r, g, b, a = colors
        except ValueError:
            print("Could not parse colors string ", colors)
            raise

        colormap_list.append((float(r), float(g), float(b)))

    colormap = branca.colormap.LinearColormap(
        colors=colormap_list,
        vmin=minimum, vmax=maximum)
    colormap.caption = dataset_info['data']['units']
    return colormap._repr_html_()


class DataportalColorbar(ipywidgets.HTML):
    def __init__(self, *args, **kwargs):
        ipywidgets.HTML.__init__(self, *args, **kwargs)
        self.dataset_colormaps = {}
        for dataset_key, data in DATASET_DIRECTORY.items():
            self.dataset_colormaps[dataset_key] = _dataset_colors_html(
                dataset_key)

    def set_colorbar_by_dataset(self, dataset_key):
        self.value = self.dataset_colormaps[dataset_key]


class DataportalMap(ipyleaflet.Map):
    def __init__(self, *args, **kwargs):
        ipyleaflet.Map.__init__(self, *args, **kwargs)

        self.active_tile_layer = None
        self.bbox_layer = None

        # Custom widgets
        self.colorbar_html = DataportalColorbar()
        self.layers_dropdown = ipywidgets.Dropdown(
            options=[
                (data['title'], dataset_key)
                for (dataset_key, data) in DATASET_DIRECTORY.items()],
            description='Preview layer'
        )
        self.layers_dropdown.observe(self.change_tile_layer, names='value')

        # Set up map controls
        for name, control in [
                ('scalebar', ipyleaflet.ScaleControl(position='bottomleft')),
                ('colorbar', ipyleaflet.WidgetControl(
                    widget=self.colorbar_html, position='topright')),
                ('layer_select', ipyleaflet.WidgetControl(
                    widget=self.layers_dropdown, position='topright')),
                ]:
            self.__setattr__(name, control)
            self.add_control(control)

        # it's easier to define this control outside the block above.
        self.drawcontrol = ipyleaflet.DrawControl(
            polyline={}, circlemarker={}, polygon={},
            rectangle={
                "shapeOptions": {
                    "fillColor": "#6be5c3",
                    "color": "#14f0fc",
                    "fillOpacity": 0.5
                },
                "drawError": {
                    "color": "#dd253b",
                    "message": "Whoops!"
                },
                "allowIntersection": False
            })
        self.add_control(self.drawcontrol)
        #self.drawcontrol.on_draw(self.draw_polygon_bbox)
        self.drawcontrol.on_draw(self.erase_old_boxes)

        if 'initial_layer' in kwargs:
            self.change_tile_layer({'new': kwargs['initial_layer']})

    def change_tile_layer(self, change):
        if self.active_tile_layer:
            self.remove_layer(self.active_tile_layer)

        layername = change['new']
        selected_data = DATASET_DIRECTORY[layername]
        self.active_tile_layer = ipyleaflet.TileLayer(
            url=(f"{DATASETS_BASE_URL}/{layername}/"
                 f"{selected_data['xyztiles']}/"
                 "{z}/{x}/{y}.png"),
            min_zoom=1,
            max_zoom=10,
            min_native_zoom=1,
            max_native_zoom=8,
            attribution=selected_data['data'].get('attribution', 'TBD'),
            show_loading=True,
        )
        self.add_layer(self.active_tile_layer)
        self.colorbar_html.set_colorbar_by_dataset(layername)
        self.layers_dropdown.value = layername

    def erase_old_boxes(self, control, **kwargs):
        self.drawcontrol.clear_rectangles()
        self.bbox_layer = interactive_options.leaflet_rectangle_from_bbox(
            kwargs['geo_json']['geometry'])

    def draw_polygon_bbox(self, control, **kwargs):
        if self.bbox_layer:
            self.remove_layer(self.bbox_layer)
        if kwargs['geo_json']['geometry']['coordinates']:
            bbox_layer = interactive_options.leaflet_rectangle_from_bbox(
                kwargs['geo_json']['geometry'])
            self.bbox_layer = bbox_layer
            self.add_layer(bbox_layer)

    def selected_bbox(self):
        if self.bbox_layer is None:
            return None
        (ulx, uly), (llx, lly) = self.bbox_layer.bounds
        return shapely.geometry.box(ulx, llx, uly, lly)

    def selected_map(self):
        if self.active_tile_layer is None:
            return None
        return self.layers_dropdown.value
