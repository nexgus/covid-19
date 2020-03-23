# A Simple COVID-19 Choropleth
Data source: https://www.worldometers.info/coronavirus

## Install Dependencies
```python
pip install -r requirements.txt
```

## Syntax
```
usage: covid-19.py [-h] [--key {active,total,death,recovered}] [--log]
                   [--debug]

NCOVID-19 Breakout.

optional arguments:
  -h, --help            show this help message and exit
  --key {active,total,death,recovered}
                        Use total to select color. (default: active)
  --log                 Log color. (default: False)
  --debug               For debug only. (default: False)
```
