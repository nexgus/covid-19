#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""Choropleth of COVID-19 Status
Ref: https://towardsdatascience.com/a-complete-guide-to-an-interactive-geographical-map-using-python-f4c5197e23e0
World map shape files: https://www.naturalearthdata.com/downloads/
"""

import geopandas as gpd
import os
import pandas as pd

from api import NovelCOVIDApi
from bokeh.models import ColorBar
from bokeh.models import GeoJSONDataSource
from bokeh.models import HoverTool
from bokeh.models import LinearColorMapper
from bokeh.models import LogColorMapper
from bokeh.plotting import figure
from bokeh.plotting import show
from colorcet import CET_L18 as palette

##############################################################################################################
KEYS = ['cases', 'deaths', 'recovered', 'active', 'casesPerMillion', 'deathsPerMillion']

##############################################################################################################
def main(args):
    # Read world geometry data
    filepath = os.path.join(args.geodir, f'ne_{args.res}m_admin_0_countries.shp')
    world = gpd.read_file(filepath)[['ADMIN', 'ADM0_A3', 'geometry']]
    world.columns = ['country', 'country_code', 'geometry'] # Rename columns
    # to-do: Do we need to remove Antarctica?
    # antarctica = world.index[world['country']=='Antarctica'][0]
    # world = world.drop(world.index[antarctica])

    # Collect world summary for graph title.
    data = NovelCOVIDApi.get_all()
    updated = NovelCOVIDApi.to_datetime(data['updated']).astimezone().isoformat()
    title = 'COVID-19 Breakout ({} {}) Cases: {}, Deaths: {}, Recovered: {}'.format(
        updated, args.key, data['cases'], data['deaths'], data['recovered'])

    # Collect data for each country.
    data = NovelCOVIDApi.get_countries()
    info = {
        'iso3': [],
        #'flag': [],
        'cases': [],
        'deaths': [],
        'recovered': [],
        'active': [],
        'casesPerMillion': [],
        'deathsPerMillion': [],
    }
    for country in data:
        info['iso3'].append(country['countryInfo']['iso3'])
        #info['flag'].append(country['countryInfo']['flag'])
        info['cases'].append(country['cases'])
        info['deaths'].append(country['deaths'])
        info['recovered'].append(country['recovered'])
        info['active'].append(country['active'])
        info['casesPerMillion'].append(country['casesPerOneMillion'])
        info['deathsPerMillion'].append(country['deathsPerOneMillion'])
    df = pd.DataFrame(info)
    high = int(df.quantile(args.high).get(args.key))

    # Merge datum into world geometry database
    world = world.merge(df, left_on='country_code', right_on='iso3', how='left')
    world.fillna('No data', inplace=True)
    del df, info

    geo = GeoJSONDataSource(geojson=world.to_json())
    del world

    if args.log:
        low = 100
        ColorMapper = LogColorMapper
    else:
        low = 0
        ColorMapper = LinearColorMapper
    color_mapper = ColorMapper(palette=palette, low=low, high=high, nan_color='#d9d9d9')

    tick_labels = {
        f'{low}': f'{low}',
        f'{high}': f'> {high}',
    }

    # The aspect ratio of Mercator projection is 1.65.
    # https://en.wikipedia.org/wiki/Mercator_projection
    fig_height = 800
    fig_width = int(fig_height * 1.65)

    color_bar = ColorBar(
        color_mapper=color_mapper, 
        label_standoff=8, 
        width=fig_width, 
        height=20,
        border_line_color=None,
        location=(0, 0), 
        orientation='horizontal',
        major_label_overrides=tick_labels,
    )

    fig = figure(
        title=title,
        plot_width=fig_width, 
        plot_height=fig_height, 
        toolbar_location='left',
    )
    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None
    fig.patches(
        'xs', 'ys', 
        source=geo,
        fill_color={
            'field': args.key, 
            'transform': color_mapper,
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
    ]))
    fig.add_layout(color_bar, 'below')
    show(fig)

##############################################################################################################
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='NCOVID-19 Breakout.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--key',  help='Use total to select color.', choices=KEYS, default='active')
    parser.add_argument('--log',  help='Log color scale.', action='store_true')
    parser.add_argument('--high', help='High clamp value for color transform, in percentile.', type=float, default=0.95)
    parser.add_argument('--geodir', help='Directory of geometry databases.', default='./geo_data')
    parser.add_argument('--res',  help='Resolution (meter) of map.', choices=[10, 50], default=50)
    args = parser.parse_args()

    main(args)
