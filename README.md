# A Simple COVID-19 Choropleth
Data source: [WorldMeter](https://www.worldometers.info/coronavirus)  
API: [NovelCOVID API](https://github.com/NovelCOVID/API)  
API Document: https://documenter.getpostman.com/view/8854915/SzS7R6uu?version=latest  

## Install Dependencies
### Linux
```python
pip install -r requirements.txt
```
### Windows
**to-do: need extra process?**
```python
pip install -r requirements.txt
```

## Syntax
```
usage: choropleth.py [-h]
                     [--key {cases,deaths,recovered,active,casesPerMillion,deathsPerMillion}]
                     [--log] [--high HIGH] [--geodir GEODIR] [--res {10,50}]

NCOVID-19 Breakout.

optional arguments:
  -h, --help            show this help message and exit
  --key {cases,deaths,recovered,active,casesPerMillion,deathsPerMillion}
                        Use total to select color. (default: active)
  --log                 Log color scale. (default: False)
  --high HIGH           High clamp value for color transform, in percentile.
                        (default: 0.95)
  --geodir GEODIR       Directory of geometry databases. (default: ./geo_data)
  --res {10,50}         Resolution (meter) of map. (default: 50)
```
