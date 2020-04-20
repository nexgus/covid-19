# A Simple COVID-19 Choropleth
Data source: [WorldMeter](https://www.worldometers.info/coronavirus)  
API: [NovelCOVID API](https://github.com/NovelCOVID/API)  
API Document: https://documenter.getpostman.com/view/8854915/SzS7R6uu?version=latest  

## Install Dependencies
```python
pip install -r requirements.txt
```

## Syntax
```
usage: covid-19.py [-h]
                   [--key {cases,deaths,recovered,active,casesPerMillion,deathsPerMillion}]
                   [--log]

NCOVID-19 Breakout.

optional arguments:
  -h, --help            show this help message and exit
  --key {cases,deaths,recovered,active,casesPerMillion,deathsPerMillion}
                        Use total to select color. (default: active)
  --log                 Log color. (default: False)
```
