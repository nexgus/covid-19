#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""Choropleth of COVID-19 Status
(1) https://towardsdatascience.com/a-complete-guide-to-an-interactive-geographical-map-using-python-f4c5197e23e0
(2) https://towardsdatascience.com/how-to-create-an-interactive-geographic-map-using-python-and-bokeh-12981ca0b567
(3) https://towardsdatascience.com/data-visualization-with-bokeh-in-python-part-ii-interactions-a4cf994e2512
(4) World map shape files: https://www.naturalearthdata.com/downloads/
"""

import geopandas as gpd
import os
import pandas as pd
import sys

from api import NovelCOVIDApi
from bokeh.models import ColorBar
from bokeh.models import GeoJSONDataSource
from bokeh.models import HoverTool
from bokeh.models import LinearColorMapper
from bokeh.models import LogColorMapper
from bokeh.plotting import figure
from colorcet import CET_L18 as PALETTE
from numpy import nan as NaN

####################################################################################################
_KEYS = ['cases', 'deaths', 'recovered', 'active', 'casesPerMillion', 'deathsPerMillion']

#####################################################################################################
class DataSource(object):
    def __init__(self, key='active', res=50, geo_dir='./geo_data', no_antarctica=False, percentile=0.95, log_color_bar=False):
        if key not in _KEYS:
            raise ValueError(f'Invalid key value. Must be one of {_KEYS}.')
        if res not in (10, 50):
            raise ValueError('Resolution of world geometry must be either 50 or 10.')
        if percentile <= 0 or percentile >= 1:
            raise ValueError('Percentile must between 0 and 1.')

        self._percentile = percentile
        self._geo = None
        self._title = self._get_title()
        self._world = self._get_world(res, geo_dir, no_antarctica)
        self._world = self._merge_status(self._world)
        self.set_key(key)
        self.fig = self._get_figure(log_color_bar)

    def _merge_status(self, world):
        data = NovelCOVIDApi.get_countries()
        info = {
            'iso3': [],
            'cases': [],
            'deaths': [],
            'recovered': [],
            'active': [],
            'casesPerMillion': [],
            'deathsPerMillion': [],
        }
        for country in data:
            info['iso3'].append(country['countryInfo']['iso3'])
            info['cases'].append(country['cases'])
            info['deaths'].append(country['deaths'])
            info['recovered'].append(country['recovered'])
            info['active'].append(country['active'])
            info['casesPerMillion'].append(country['casesPerOneMillion'])
            info['deathsPerMillion'].append(country['deathsPerOneMillion'])
        df = pd.DataFrame(info)
        world = world.merge(df, left_on='country_code', right_on='iso3', how='left')
        world.fillna('No data', inplace=True)
        return world

    def _get_color_scale_high_limit(self, percentile):
        df = pd.DataFrame(self._world['key'])
        df.replace(to_replace='No data', value=NaN, inplace=True)
        return int(df.quantile(percentile).get('key'))

    def _get_figure(self, log_color_bar):
        # The aspect ratio of Mercator projection is 1.65.
        # https://en.wikipedia.org/wiki/Mercator_projection
        plot_height = 800
        plot_width = int(plot_height * 1.65)

        color_high_limit = self._high
        color_low_limit = 0
        ColorMapper = LinearColorMapper
        if log_color_bar:
            color_low_limit = 100
            ColorMapper = LogColorMapper

        self._color_mapper = ColorMapper(
            palette=PALETTE, 
            low=color_low_limit, 
            high=color_high_limit, 
            nan_color='#d9d9d9'
        )

        self._color_bar = ColorBar(
            color_mapper=self._color_mapper, 
            label_standoff=8, 
            width=20, 
            height=int(plot_height*0.9),
            border_line_color=None,
            location=(0, 0), 
            orientation='vertical',
            major_label_overrides={
                f'{color_low_limit}': f'{color_low_limit}',
                f'{color_high_limit}': f'{color_high_limit}+',
            },
        )

        fig = figure(
            title=self._title.replace('<key>', self.key),
            plot_width=plot_width, 
            plot_height=plot_height, 
            toolbar_location='left',
        )
        fig.xgrid.grid_line_color = None
        fig.ygrid.grid_line_color = None
        fig.patches(
            'xs', 'ys', 
            source=self._geo,
            fill_color={
                'field': 'key', 
                'transform': self._color_mapper,
            },
            color='black',
            line_width=0.3, 
        )
        fig.add_tools(
            HoverTool(tooltips=[
                ('Country', '@country'),
                ('Cases', '@cases'),
                ('Deaths', '@deaths'),
                ('Recovered', '@recovered'),
                ('Active', '@active'),
                ('Cases/Million', '@casesPerMillion'),
                ('Deaths/Million', '@deathsPerMillion'),
            ]),
        )
        fig.add_layout(self._color_bar, 'right')

        return fig

    def _get_title(self):
        data = NovelCOVIDApi.get_all()
        updated = NovelCOVIDApi.to_datetime(data['updated']).astimezone().isoformat()
        title = 'COVID-19 Breakout (<key> @ {}) Cases: {}, Deaths: {}, Recovered: {}'.format(
            updated, data['cases'], data['deaths'], data['recovered'])
        return title

    def _get_world(self, res, geo_dir, no_antarctica=False):
        filepath = os.path.join(geo_dir, f'ne_{res}m_admin_0_countries.shp')
        world = gpd.read_file(filepath)[['ADMIN', 'ADM0_A3', 'geometry']]
        world.columns = ['country', 'country_code', 'geometry'] # Rename columns
        if no_antarctica:
            antarctica = world.index[world['country']=='Antarctica'][0]
            world = world.drop(world.index[antarctica])
        return world

    def set_key(self, key):
        if key not in _KEYS:
            raise ValueError(f'Invalid key value. Must be one of {_KEYS}.')
        self._world['key'] = self._world[key]
        self.key = key
        self._high = self._get_color_scale_high_limit(self._percentile)
        if self._geo is None:
            self._geo = GeoJSONDataSource(geojson=self._world.to_json())
        else:
            self._geo.geojson = self._world.to_json()

        if hasattr(self, 'fig'):
            self._color_mapper.high = self._high
            self.fig.title.text = self._title.replace('<key>', self.key)

#####################################################################################################
if __name__ == '__main__':
    # Non-Interactive mode
    import argparse
    from bokeh.io import show

    parser = argparse.ArgumentParser(description='NCOVID-19 Breakout.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-k', '--key',  
                        choices=_KEYS, 
                        default='active', 
                        help='Use total to select color.')
    parser.add_argument('-l', '--log',
                        action='store_true', 
                        help='Color bar in log scale.')
    parser.add_argument('-p', '--percentile', 
                        type=float, 
                        default=0.95,
                        help='Percentile for high limit of color bar.')
    parser.add_argument('-d', '--geodir', 
                        default='./geo_data', 
                        help='Directory of geometry databases.')
    parser.add_argument('-r', '--res', 
                        choices=[10, 50], 
                        default=50, 
                        help='Resolution (meter) of map.')
    parser.add_argument('-n', '--no-antarctica', 
                        action='store_true', 
                        help='Do not display Antarctica.')
    args = parser.parse_args()

    ds = DataSource(
        key=args.key, 
        res=args.res, 
        geo_dir=args.geodir, 
        no_antarctica=args.no_antarctica, 
        percentile=args.percentile, 
        log_color_bar=args.log
    )
    show(ds.fig)

else:
    # Interactive mode.
    # bokeh serve --show choropleth.py
    # to-do: can we make it standalone mode? which means we have to write javascript
    from bokeh.io import curdoc
    from bokeh.layouts import widgetbox
    from bokeh.layouts import column
    from bokeh.models import RadioButtonGroup

    ds = DataSource()

    def radio_buttons_on_click(idx):
        global ds
        ds.set_key(_KEYS[idx])

    radio_buttons = RadioButtonGroup(
        labels=_KEYS,
        active=_KEYS.index('active'),
    )
    radio_buttons.on_click(radio_buttons_on_click)

    layout = column(ds.fig, column(radio_buttons))
    curdoc().add_root(layout)
