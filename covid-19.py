#!/usr/bin/env python
# -*- coding=utf-8 -*-
import argparse
import iso3166
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go
import requests

from bs4 import BeautifulSoup

##############################################################################################################
SRCURL = 'https://www.worldometers.info/coronavirus'
KEYS = ['active', 'total', 'death', 'recovered']
CORRECTION = {
    'Iran':                     'IRN', # 'Iran, Islamic Republic Of',
    'USA':                      'USA', # 'United States Of America',
    'S. Korea':                 'KOR', # 'Korea, Republic Of',
    'UK':                       'GBR', # 'United Kingdom of Great Britain and Northern Ireland',
    'Russia':                   'RUS', # 'Russian Federation',
    'UAE':                      'ARE', # 'United Arab Emirates',
    'Vietnam':                  'VNM', # 'Viet Nam',
    'Brunei':                   'BRN', # 'Brunei Darussalam',
    'Faeroe Islands':           'FRO', # 'Faroe Islands',
    'Moldova':                  'MDA', # 'Moldova, Republic Of',
    'Venezuela':                'VEN', # 'Venezuela, Bolivarian Republic Of',
    'Bolivia':                  'BOL', # 'Bolivia, Plurinational State Of',
    'Ivory Coast':              'CIV', # "Côte d'Ivoire",
    'DRC':                      'COD', # 'Congo, Democratic Republic Of The',
    'St. Barth':                'BLM', # 'Saint Barthélemy',
    'Saint Martin':             'MAF', # 'Saint Martin (French Part)',
    'Tanzania':                 'TZA', # 'Tanzania, United Republic Of',
    'U.S. Virgin Islands':      'VIR', # 'Virgin Islands, U.S.',
    'CAR':                      'BES', # 'Bonaire, Sint Eustatius and Saba',
                                       # Caribbean Netherlands – See Bonaire, Sint Eustatius and Saba.
    'Vatican City':             'VAT', # 'Holy See',
    'St. Vincent Grenadines':   'VCT', # 'Saint Vincent And The Grenadines',
    'Sint Maarten':             'SXM', # 'Sint Maarten (Dutch Part)',
    'Syria':                    'SYR', # 'Syrian Arab Republic'
    'Turks and Caicos':         'TCA', # 'Turks and Caicos Islands'
}

##############################################################################################################
def add_country_code(data):
    indices_no_cc = [] # indices for no country code
    data['country_code'] = []
    data['country_name'] = [] # country.apolitical_name
    for idx, country in enumerate(data['country']):
        try:
            country = iso3166.countries.get(country)
        except KeyError:
            if country in CORRECTION:
                country = iso3166.countries.get(CORRECTION[country])
            else:
                if country == 'Channel Islands':
                    # Treat Channel Islands as a part of UK
                    # https://en.wikipedia.org/wiki/Channel_Islands
                    idx_uk = data['country'].index('UK')
                    data['total'][idx_uk]     += data['total'][idx]    
                    data['death'][idx_uk]     += data['death'][idx]    
                    data['recovered'][idx_uk] += data['recovered'][idx]
                    data['active'][idx_uk]    += data['active'][idx]   
                elif country == 'Diamond Princess':
                    # Not a country
                    # https://en.wikipedia.org/wiki/Diamond_Princess_(ship)
                    pass
                else:
                    print(f'"{country}" is not in ISO3166 country names. Remove it.')
                indices_no_cc.append(idx)
                continue
        data['country_code'].append(country.alpha3)
        data['country_name'].append(country.apolitical_name)

    indices_no_cc.sort(reverse=True)
    for idx in indices_no_cc:
        data['country'].pop(idx)
        data['total'].pop(idx)
        data['death'].pop(idx)
        data['recovered'].pop(idx)
        data['active'].pop(idx)

    return data

##############################################################################################################
def collect_data(table):
    data = { # Just for store data from source
        'country':   [],
        'total':     [],
        'active':    [],
        'death':     [],
        'recovered': [],
    }

    for tr in table.tbody.find_all('tr'):
        td = tr.find_all('td')
        data['country'].append(td[0].string.strip())
        data['total'].append(to_number(td[1].string))
        data['death'].append(to_number(td[3].string))
        data['recovered'].append(to_number(td[5].string))
        data['active'].append(to_number(td[6].string))

    return data

##############################################################################################################
def get_title(soup, key):
    div = soup.find('div', {'id': 'page-top'})
    header = f'{div.string.strip()} ({key})'
    srcurl = f'Source: <a href="{SRCURL}">Worldmeter</a>'
    div = div.find_next()
    updated = div.string.strip()
    return '<br>'.join([header, srcurl, updated])

##############################################################################################################
def save(filepath, x):
    dirname = os.path.dirname(filepath)
    os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as fp:
        fp.write(x.prettify())

##############################################################################################################
def to_number(number, ntype=int):
    if number is None: return ntype(0)
    number = number.strip().replace(',', '')
    if number == '': return ntype(0)
    return ntype(number)

##############################################################################################################
def main(args):
    r = requests.get(SRCURL)
    soup = BeautifulSoup(r.text, 'html.parser')
    if args.debug: save('./html/soup.html', soup)

    title = get_title(soup, args.key)

    table = soup.find('table', {'id': 'main_table_countries_today'})
    if args.debug: save('./html/table.html', table)

    data = collect_data(table)
    data = add_country_code(data)
    df = pd.DataFrame(data)

    if args.log:
        df['log'] = np.ma.log(df[args.key].to_numpy().astype(float))
        args.key = 'log'

    df['hover_text'] = (
        df['country_name'] + 
        '<br>Total: '     + df['total'].astype(str) + 
        '<br>Active: '    + df['active'].astype(str) +
        '<br>Deaths: '    + df['death'].astype(str) +
        '<br>Recovered: ' + df['recovered'].astype(str)
    )
    fig = go.Figure(
        data=go.Choropleth(
            locations=df['country_code'],
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
    parser.add_argument('--debug', help='For debug only.', action='store_true')
    args = parser.parse_args()

    main(args)
