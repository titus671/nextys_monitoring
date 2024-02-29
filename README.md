## What is the point of this repo?

This is a set of scripts for storing the metrics
from the Nextys dcw20 in a timescale database

## Installation guide

1. clone the repo
 - `git clone https://github.com/titus672/nextys_monitoring.git`
2. update and install prereqs
 - `sudo apt update && sudo apt install python3.11-venv python3-dev libpq-dev`
3. move into the repo and create the python virtual environment
 - `cd nextys_monitoring`
 - `python3 -m venv venv`
4. activate the virtual environment and install python prereqs
```
. venv/bin/activate
pip install -r requirements.txt
```
### Configuration guide

1. cd into the src dir and configure the program
```
cd src
cp config_example.json config.json
vim config.json
python lib/psql_functions.py -v
```
2. copy the `nextys_monitor.service` file and enable it
```
sudo cp nextys_monitor.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now nextys_monitor
```
