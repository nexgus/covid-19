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
}

##############################################################################################################
def get_number(number, ntype=int):
    if number is None: return ntype(0)
    number = number.strip().replace(',', '')
    if number == '': return ntype(0)
    return ntype(number)

##############################################################################################################
def get_stats(table):
    stats = {
        'country_name': [],
        'country_code': [],
        'total':     [],
        'active':    [],
        'death':     [],
        'recovered': [],
    }

    for tr in table.tbody.find_all('tr'):
        td = tr.find_all('td')
        country   = td[0].string.strip()
        total     = get_number(td[1].string) # total cases
        death     = get_number(td[3].string) # total deaths
        recovered = get_number(td[5].string) # total recovered
        active    = get_number(td[6].string) # active cases

        try:
            country = iso3166.countries.get(country)
        except KeyError:
            if country in CORRECTION:
                country = CORRECTION[country]
                country = iso3166.countries.get(country)
            elif country == 'Diamond Princess':
                continue
            elif country == 'Channel Islands':
                if 'GBR' in stats['country_code']: # UK
                    idx = stats['country_code'].index('GBR')
                    stats['total'][idx]     += total
                    stats['active'][idx]    += active
                    stats['death'][idx]     += death
                    stats['recovered'][idx] += recovered
                    continue
                else:
                    country = iso3166.countries.get('GBR')
            else:
                print(f'"{country}" is not in ISO3166 country names.')
                continue

        stats['country_name'].append(country.apolitical_name)
        stats['country_code'].append(country.alpha3)
        stats['total'].append(total)
        stats['active'].append(active)
        stats['death'].append(death)
        stats['recovered'].append(recovered)

    return stats

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
def main(args):
    r = requests.get(SRCURL)
    soup = BeautifulSoup(r.text, 'html.parser')
    if args.debug: save('./html/soup.html', soup)

    title = get_title(soup, args.key)

    table = soup.find('table', {'id': 'main_table_countries_today'})
    if args.debug: save('./html/table.html', table)

    stats = get_stats(table)
    df = pd.DataFrame(data=stats)

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
