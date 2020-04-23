# A Simple COVID-19 Choropleth
Data source: [WorldMeter](https://www.worldometers.info/coronavirus)  
API: [NovelCOVID API](https://github.com/NovelCOVID/API)  
API Document: https://documenter.getpostman.com/view/8854915/SzS7R6uu?version=latest  

## Clone Source Code
```bash
cd ~
git clone https://github.com/nexgus/covid-19
```

## Install Dependencies
### Linux
```bash
cd covid-19
pip install -r requirements.txt
```
### Windows 10
1.  Download `GDAL` wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal) and install.  
    You have to select correct one. For example, `GDAL-3.0.4-cp37-cp37m-win_amd64.whl` for Python 3.7 and Window 10.  
    You may install `GDAL` by using `pip install <path to your wheel file>`:  
    ```batch
    pip install GDAL-3.0.4-cp37-cp37m-win_amd64.whl
    ```
1.  Download `fiona` wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona) and install.  
    You have to select correct one. For example, `Fiona-1.8.13-cp37-cp37m-win_amd64.whl` for Python 3.7 and Windows 10.  
    You may install `GDAL` by using `pip install <path to your wheel file>`:  
    ```batch
    pip install Fiona-1.8.13-cp37-cp37m-win_amd64.whl
    ```
1.  ```batch
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
