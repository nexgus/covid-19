#!/usr/bin/env python
# -*- coding=utf-8 -*-
import datetime
import requests

####################################################################################################
class NovelCOVIDApi(object):
    """API for Current cases and more stuff about COVID-19 or the Novel Coronavirus Strain.
    Website: https://github.com/NovelCOVID/API
    Doc: https://documenter.getpostman.com/view/8854915/SzS7R6uu?version=latest
    """

    @staticmethod
    def to_datetime(ms):
        """Convert milliseconds to datetime
        """
        return datetime.datetime.fromtimestamp(ms/1000)

    @staticmethod
    def get_all():
        """Returns all total cases, recovery, and deaths.
        Example returned dict:
            ```{
                'updated': 1587523475904, 
                'cases': 2557181, 
                'todayCases': 1421, 
                'deaths': 177641, 
                'todayDeaths': 182, 
                'recovered': 690444, 
                'active': 1689096, 
                'critical': 57245, 
                'casesPerOneMillion': 328, 
                'deathsPerOneMillion': 22, 
                'tests': 22638528, 
                'testsPerOneMillion': 2903.8, 
                'affectedCountries': 212
            }```
        """
        r = requests.get('https://corona.lmao.ninja/v2/all')
        if not r.ok:
            raise ValueError(f'NovelCOVIDApi.get_all() error: {r.status_code} {r.reason}')
        return r.json()

    @staticmethod
    def get_countries():
        """Returns data of all countries that has COVID-19.
        Example returned list:
            ```
            [
                {
                    'updated': 1587524076430, 
                    'country': 'Taiwan', 
                    'countryInfo': {
                        '_id': 158, 
                        'iso2': 'TW', 
                        'iso3': 'TWN', 
                        'lat': 23.5, 
                        'long': 121, 
                        'flag': 'https://raw.githubusercontent.com/NovelCOVID/API/master/assets/flags/tw.png'
                    }, 
                    'cases': 425, 
                    'todayCases': 0, 
                    'deaths': 6, 
                    'todayDeaths': 0, 
                    'recovered': 217, 
                    'active': 202, 
                    'critical': 0, 
                    'casesPerOneMillion': 18, 
                    'deathsPerOneMillion': 0, 
                    'tests': 55476, 
                    'testsPerOneMillion': 2329, 
                    'continent': 'Asia'
                },
                ...
            ]
            ```
        """
        r = requests.get('https://corona.lmao.ninja/v2/countries?sort=country')
        if not r.ok:
            raise ValueError(f'NovelCOVIDApi.get_countries() error: {r.status_code} {r.reason}')
        return r.json()

    @staticmethod
    def get_country(country):
        """Returns data of a specific country.
        Example return dict:
        ```
        {
            'updated': 1587525277162, 
            'country': 'Taiwan', 
            'countryInfo': {
                '_id': 158, 
                'iso2': 'TW', 
                'iso3': 'TWN', 
                'lat': 23.5, 
                'long': 121, 
                'flag': 'https://raw.githubusercontent.com/NovelCOVID/API/master/assets/flags/tw.png'
            }, 
            'cases': 425, 
            'todayCases': 0, 
            'deaths': 6, 
            'todayDeaths': 0, 
            'recovered': 217, 
            'active': 202, 
            'critical': 0, 
            'casesPerOneMillion': 18, 
            'deathsPerOneMillion': 0, 
            'tests': 55476, 
            'testsPerOneMillion': 2329, 
            'continent': 'Asia'
        }
        ```
        """
        r = requests.get(f'https://corona.lmao.ninja/v2/countries/{country}')
        if not r.ok:
            raise ValueError(f'NovelCOVIDApi.get_country() error: {r.status_code} {r.reason}')
        json = r.json()
        if 'message' in json:
            raise ValueError(f'NovelCOVIDApi.get_country() error: {json["message"]}')
        return json

    @staticmethod
    def get_states():
        """Returns all United States of America and their Corona data.
        Example returned list:
        ```
        [
            {
                'state': 'New York', 
                'cases': 256555, 
                'todayCases': 0, 
                'deaths': 19693, 
                'todayDeaths': 0, 
                'active': 207269, 
                'tests': 649325, 
                'testsPerOneMillion': 33098
            },
            ...
        ]
        ```
        """
        r = requests.get('https://corona.lmao.ninja/v2/states')
        if not r.ok:
            raise ValueError(f'NovelCOVIDApi.get_states() error: {r.status_code} {r.reason}')
        return r.json()

    @staticmethod
    def get_john_hopkins_csse_data():
        """Return data from the John Hopkins CSSE Data Repository (Provinces and such).
        Example returned list:
        ```
        [
            {
                'country': 'US', 
                'province': 'Diamond Princess', 
                'updatedAt': '2020-04-21 23:30:50', 
                'stats': {
                    'confirmed': 49, 
                    'deaths': 0, 
                    'recovered': 0
                }, 
                'coordinates': {
                    'latitude': '', 
                    'longitude': ''
                }
            },
            ...
        ]
        ```
        """
        r = requests.get('https://corona.lmao.ninja/v2/jhucsse')
        if not r.ok:
            raise ValueError(f'NovelCOVIDApi.get_john_hopkins_csse_data() error: {r.status_code} {r.reason}')
        return r.json()

    @staticmethod
    def get_historical_data():
        """Get historical data from the start of 2020. (JHU CSSE GISand Data).
        """
        r = requests.get('https://corona.lmao.ninja/v2/historical')
        if not r.ok:
            raise ValueError(f'NovelCOVIDApi.get_historical_data() error: {r.status_code} {r.reason}')
        return r.json()
