# Using Dash in Python to visualize real time data from https://www.bayut.com/
# Visit this link to see the final output of the project :- https://kazi-bayout.herokuapp.com/


# SOA Scraper Library
ma
## Setup Instructions

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Setup Microsoft Presido
If document anonymizing is required, please run the following on a your local docker.
```sh
docker run -d -p 5002:3000 mcr.microsoft.com/presidio-anonymizer:latest
docker run -d -p 5001:3000 mcr.microsoft.com/presidio-analyzer:latest
```

## CLI

You can invoke the CLI using
```
$ ./src/scraper-cli                                                                    
usage: ./main.py <command> [<args>]
   _____               _ _            _   
  / ____|             | (_)          | |  
 | |  __ _ __ __ _  __| |_  ___ _ __ | |_ 
 | | |_ | '__/ _` |/ _` | |/ _ \ '_ \| __|
 | |__| | | | (_| | (_| | |  __/ | | | |_ 
  \_____|_|  \__,_|\__,_|_|\___|_| |_|\__|

Available commands:
    help        show this help message and exit
    scrape      scrape html document and produce JSON
    split       split input HTML to multiple files
    anonymize   anonymize input HTML (Microsft Presido Is Required)
scraper-cli: error: the following arguments are required: command
```

## Development Instructions

### Test Running

```sh
make test
```

### CLI in dev mode
```sh
export PYTHONPATH=./src
./bin/scraper-cli
```

## Folder Structure

```
.
├── Makefile
├── README.md
├── main.py
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── models/
│   ├── processors/
│   └── utils/
└── tests/
    ├── __pycache__/
    └── test_utils.py

6 directories, 6 files
```
