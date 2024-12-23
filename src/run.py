#!/usr/bin/env python3
from lib.nextys import NEXTYS
from lib.config import CONFIG
from lib.psql_functions import DB, init_connection
from lib.logger import Logger
import json, time, signal, sys
from vigil_reporter.reporter import VigilReporter

def gracefull_shutdown(sig, frame):
    print("\nexiting")
    sys.exit(0)

def pprint(j):
    print(json.dumps(j, indent=2))

def avg(l: list):
    return round(sum(l) / len(l), 3)

def get_metrics():
    signal.signal(signal.SIGINT, gracefull_shutdown)
    metrics = []
    config = CONFIG()
    nexty = NEXTYS(config)
    count = 0
    t1 = time.time() + 10
    while time.time() <= t1:
        metrics.append(nexty.read_meters())
        count += 1
        time.sleep(0.1)
    f = {
        "device_id": [],
        "unix_timestamp": [],
        "input_voltage": [],
        "input_current": [],
        "output_voltage": [],
        "output_current": [],
        "batt_voltage": [],
        "batt_current": [],
        "batt_int_resistance": [],
        "batt_charge_capacity": [],
        "operating_time": [],
        "batt_operating_time": []
    }
    accepted_keys = [
        "device_id",
        "unix_timestamp",
        "input_voltage",
        "input_current",
        "output_voltage",
        "output_current",
        "batt_voltage",
        "batt_current",
        "batt_int_resistance",
        "batt_charge_capacity",
        "operating_time",
        "batt_operating_time"
    ]
    
    for metric in metrics:
        for key in metric:
            if key in accepted_keys:
                f[key].append(metric[key])
    # creates a dictionary with the following schema...
    # {
    #     "device_id": [device_id],
    #     "unix_timestamp": [list of unix_timestamps],
    #     "input_voltage": [list of input_voltages],
    #     "input_current": [list of input_currents],
    #     ...
    # }
    return {
        "device_id": f["device_id"][0],
        "unix_timestamp": avg(f["unix_timestamp"]),
        "input_voltage_min": min(f["input_voltage"]),
        "input_voltage_avg": avg(f["input_voltage"]),
        "input_voltage_max": max(f["input_voltage"]),
        "input_current_min": min(f["input_current"]),
        "input_current_avg": avg(f["input_current"]),
        "input_current_max": max(f["input_current"]),
        "output_voltage_min": min(f["output_voltage"]),
        "output_voltage_avg": avg(f["output_voltage"]),
        "output_voltage_max": max(f["output_voltage"]),
        "output_current_min": min(f["output_current"]),
        "output_current_avg": avg(f["output_current"]),
        "output_current_max": max(f["output_current"]),
        "batt_voltage_min": min(f["batt_voltage"]),
        "batt_voltage_avg": avg(f["batt_voltage"]),
        "batt_voltage_max": max(f["batt_voltage"]),
        "batt_current_min": min(f["batt_current"]),
        "batt_current_avg": avg(f["batt_current"]),
        "batt_current_max": max(f["batt_current"]),
        "batt_int_resistance": f["batt_int_resistance"][-1],
        "batt_charge_capacity": avg(f["batt_charge_capacity"]),
        "operating_time": f["operating_time"][-1],
        "batt_operating_time": f["batt_operating_time"][-1]
    }
        
def main_loop():
    config = CONFIG()
    logger = Logger()
    vigil_config = {
        "url": config.reporter_url,
        "token": config.reporter_token,
        "probe_id": config.reporter_probe_id,
        "node_id": config.reporter_node_id,
        "replica_id": config.reporter_replica_id,
        "interval": config.reporter_interval
    }
    reporter = VigilReporter.from_config(vigil_config)
    reporter.report_in_thread()

    while True:
        try:
            db = DB(init_connection(config))
            db.initialize_device(config)
            settings = NEXTYS(config).read_settings()
            db.insert_settings(settings)
            # get metrics
            metrics = get_metrics()
            logger.log(db.update_alerts(metrics))
            logger.log(db.insert_metrics(metrics))
            db.close_connection()
        except Exception as e:
            reporter.stop()
            raise e

def test():
    config = CONFIG()
    db = DB(init_connection(config))
    db.initialize_device(config)
    pprint(get_metrics())

def main():
    logger = Logger()
    config = CONFIG()
    nexty = NEXTYS(config)
    settings = nexty.read_settings()
    db = DB(init_connection(config))
    db.initialize_device(config)
    db.insert_settings(settings)
    db.close_connection()

if __name__ == "__main__":
    main_loop()

