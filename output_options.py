import logging

import ipywidgets as widgets
from osgeo import osr


# From https://ipywidgets.readthedocs.io/en/latest/examples/Output%20Widget.html
class OutputWidgetHandler(logging.Handler):
    """ Custom logging handler sending logs to an output widget """

    def __init__(self, *args, **kwargs):
        super(OutputWidgetHandler, self).__init__(*args, **kwargs)
        layout = {
            'width': '100%',
            'height': '160px',
            'border': '1px solid black'
        }
        self.out = widgets.Output(layout=layout)

    def emit(self, record):
        """ Overload of logging.Handler method """
        formatted_record = self.format(record)
        new_output = {
            'name': 'stdout',
            'output_type': 'stream',
            'text': formatted_record+'\n'
        }
        self.out.outputs = self.out.outputs + (new_output,)

    def show_logs(self):
        """ Show the logs """
        display(self.out)

    def clear_logs(self):
        """ Clear the current logs """
        self.out.clear_output()


def parse_epsg_code(epsg_code):
    if isinstance(epsg_code, int):
        # TODO: silence warnings
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg_code)
        srs_name = srs.GetName()
        if srs.IsGeographic():
            srs_units = srs.GetAngularUnitsName()
        else:
            srs_units = srs.GetLinearUnitsName()

        if srs_name in {None, 'unknown'}:
            label = f"EPSG code {epsg_code} not recognized"
            pixel_size_text = ""
        else:
            label = f"{srs_name}, Units: {srs_units}"
            pixel_size_text = f"NOTE: pixel sizes have units {srs_units}"
    else:
        label = f"EPSG code {epsg_code} not recognized"
        pixel_size_text = ""

    return label, pixel_size_text


EPSG_LABEL = widgets.Label("")  # For holding the name of the EPSG code
EPSG_INPUT = widgets.Text(
    value='4326',
    placeholder='4326',
    description='EPSG code:',
    disabled=False
)

PIXEL_SIZES_LABEL = widgets.HTML("")
PIXEL_SIZE_X_INPUT = widgets.Text(
    value='1',
    placeholder='1',
    description='Pixel X size',
    disabled=False
)
PIXEL_SIZE_Y_INPUT = widgets.Text(
    value='1',
    placeholder='1',
    description='Pixel Y size',
    disabled=False
)
