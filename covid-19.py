#!/usr/bin/env python
# -*- coding=utf-8 -*-
import argparse
import datetime
import json
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go
import requests

##############################################################################################################
API_Countries = 'https://corona.lmao.ninja/v2/countries?sort=country'
API_All = 'https://corona.lmao.ninja/v2/all'
KEYS = ['cases', 'deaths', 'recovered', 'active', 'casesPerMillion', 'deathsPerMillion']

# For detail please visit https://documenter.getpostman.com/view/8854915/SzS7R6uu?version=latest
# or https://github.com/NovelCOVID/API
API = {
    # Returns all total cases, recovery, and deaths.
    'All': 'https://corona.lmao.ninja/v2/all',
    # Returns data of all countries that has COVID-19.
    'Countries': 'https://corona.lmao.ninja/v2/countries?sort=country',
    # Returns data of a specific country.
    'Country': 'https://corona.lmao.ninja/v2/countries/<country>',
    # Returns all United States of America and their Corona data.
    'States': 'https://corona.lmao.ninja/v2/states',
    # Return data from the John Hopkins CSSE Data Repository (Provinces and such).
    'John HOpkins CSSE Data': 'https://corona.lmao.ninja/v2/jhucsse',
    # Get historical data from the start of 2020. (JHU CSSE GISand Data).
    'Historical Data': 'https://corona.lmao.ninja/v2/historical',
}

##############################################################################################################
def main(args):
    r = requests.get(API['All'])
    total = eval(r.content.decode('utf-8'))
    updated = datetime.datetime.fromtimestamp(total['updated']//1000).astimezone().isoformat()
    title = (f'COVID-19 Breakout ({args.key}) {updated}' +
             f'<br>Cases: {total["cases"]}' + 
             f'<br>Deaths: {total["deaths"]}' + 
             f'<br>Recovered: {total["recovered"]}')

    r = requests.get(API['Countries'])
    data = json.loads(r.content.decode('utf-8'))

    info = {
        'country': [],
        'iso3': [],
        'flag': [],
        'cases': [],
        'deaths': [],
        'recovered': [],
        'active': [],
        'casesPerMillion': [],
        'deathsPerMillion': [],
    }
    for country in data:
        info['country'].append(country['country'])
        info['iso3'].append(country['countryInfo']['iso3'])
        info['flag'].append(country['countryInfo']['flag'])
        info['cases'].append(country['cases'])
        info['deaths'].append(country['deaths'])
        info['recovered'].append(country['recovered'])
        info['active'].append(country['active'])
        info['casesPerMillion'].append(country['casesPerOneMillion'])
        info['deathsPerMillion'].append(country['deathsPerOneMillion'])

    df = pd.DataFrame(info)
    if args.log:
        df['log'] = np.ma.log(df[args.key].to_numpy().astype(float))
        args.key = 'log'

    df['hover_text'] = (df['country'] + 
                        '<br>Cases:     ' + df['cases'].astype(str) + 
                        '<br>Deaths:    ' + df['deaths'].astype(str) +
                        '<br>Recovered: ' + df['recovered'].astype(str) +
                        '<br>Active:    ' + df['active'].astype(str) +
                        '<br>Cases/Million:  ' + df['casesPerMillion'].astype(str) +
                        '<br>Deaths/Million: ' + df['deathsPerMillion'].astype(str))

    fig = go.Figure(
        data=go.Choropleth(
            locations=df['iso3'],
            z=df[args.key],
            colorscale = 'Reds',
            showscale=False,
            text=df['hover_text'],
        ),
        layout=go.Layout(
            title=go.layout.Title(
                text=title
            ),
            geo=go.layout.Geo(
                resolution=50,
                showcountries=True,
                showlakes=False,
            ),
        ),
    )
    fig.show()

##############################################################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NCOVID-19 Breakout.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--key',   help='Use total to select color.', choices=KEYS, default='active')
    parser.add_argument('--log',   help='Log color.', action='store_true')
    args = parser.parse_args()

    main(args)
