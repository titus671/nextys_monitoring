import psycopg
import os, sys


if __name__ == "__main__":
    from logger import Logger
else:
    from lib.logger import Logger

class DB:
    def __init__(self, conn):

        self.logger = Logger()
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except AttributeError as e:
            self.logger.log("Connection was not valid,\nconsider double checking your creds")
            raise e

    def create_tables(self):
        check_exists_sensor_metadata = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'sensor_metadata'
            )"""
        create_sensor_metadata_table = """
            CREATE TABLE sensor_metadata (
                id SERIAL PRIMARY KEY,
                ip_address INET,
                sysName VARCHAR(50),
                location VARCHAR(50),
                batt_low INT,
                ac_down INT,
                batt_type INTEGER,
                charge_voltage REAL,
                charge_current REAL,
                float_voltage REAL,
                low_voltage REAL,
                deep_discharge_voltage REAL,
                max_discharge_current REAL,
                batt_capacity REAL,
                DCDC_output_mode INTEGER
            );
            """
        check_exists_sensor_hypertable = """
            SELECT EXISTS (
                SELECT 1
                FROM _timescaledb_catalog.hypertable
                WHERE table_name = 'sensor_data'
            )
            """
        create_sensor_data_table = """
            CREATE TABLE sensor_data (
                time TIMESTAMPTZ NOT NULL,
                sensor_id INTEGER,
                input_voltage_min REAL,
                input_voltage_avg REAL,
                input_voltage_max REAL,
                input_current_min REAL,
                input_current_avg REAL,
                input_current_max REAL,
                output_voltage_min REAL,
                output_voltage_avg REAL,
                output_voltage_max REAL,
                output_current_min REAL,
                output_current_avg REAL,
                output_current_max REAL,
                batt_voltage_min REAL,
                batt_voltage_avg REAL,
                batt_voltage_max REAL,
                batt_current_min REAL,
                batt_current_avg REAL,
                batt_current_max REAL,
                batt_int_resistance REAL,
                batt_charge_capacity REAL,
                operating_time INTEGER,
                batt_operating_time INTEGER
            );
            CREATE INDEX ON sensor_data (sensor_id, time DESC);
            """
        create_sensor_data_hypertable = """
            SELECT create_hypertable('sensor_data', 'time');
            ALTER TABLE sensor_data SET (timescaledb.compress,
                                         timescaledb.compress_segmentby = 'sensor_id');
            SELECT add_compression_policy('sensor_data', INTERVAL '2 days');
            """
        self.cursor.execute(check_exists_sensor_metadata)
        if self.cursor.fetchone()[0]:
            self.logger.log("sensor_metadata table exists already")
        else:
            self.cursor.execute(create_sensor_metadata_table)
            self.logger.log("created sensor_metadata table")
        self.cursor.execute(check_exists_sensor_hypertable)
        if self.cursor.fetchone()[0]:
            self.logger.log("sensor_data hypertable exists already")
        else:
            self.cursor.execute(create_sensor_data_table)
            self.logger.log("created sensor_data table")
            self.cursor.execute(create_sensor_data_hypertable)
            self.logger.log("created sensor_data hypertable")

    def initialize_device(self, config):
        self.config = config
        values = (
            f"{config.ip_address}",
            f"{config.sysName}",
            f"{config.location}"
        )
        query = f"""
        INSERT INTO sensor_metadata (
            ip_address,
            sysname,
            location
            )
        VALUES (%s,%s,%s)
        RETURNING id;
        """
        if config.device_id is None:
            self.cursor.execute(query, values)
            id = self.cursor.fetchone()[0]
            config.set_device_id(id)
    
    def update_alerts(self, metrics):
        #expects a state dict with the following schema:
        #{
        #    "batt_low": True,
        #    "ac_down": False,
        #    "id": 1
        #}
        v = {}
        if metrics["batt_voltage_avg"] <= self.config.low_batt_threshold:
            v["low_batt"] = int(True)
        else:
            v["low_batt"] = int(False)
        if metrics["input_voltage_avg"] <= self.config.ac_down_threshold:
            v["ac_down"] = int(True)
        else:
            v["ac_down"] = int(False)
        v["id"] = self.config.device_id
        
        query = f"""
        UPDATE sensor_metadata
            SET batt_low = %s, ac_down = %s
        WHERE id = %s;
        """
        return self.cursor.execute(query, (v["low_batt"], v["ac_down"], v["id"]))
 
    def insert_settings(self, settings: dict):
        values = (
            settings["device_id"],
            settings["ip_address"],
            settings["sysName"],
            settings["location"],
            settings['batt_type'],
            settings['charge_voltage'],
            settings['charge_current'],
            settings['float_voltage'],
            settings['low_voltage'],
            settings['deep_discharge_voltage'],
            settings['max_discharge_current'],
            settings['batt_capacity'],
            settings['DCDC_output_mode'],
            settings["ip_address"],
            settings["sysName"],
            settings["location"],
            settings['batt_type'],
            settings['charge_voltage'],
            settings['charge_current'],
            settings['float_voltage'],
            settings['low_voltage'],
            settings['deep_discharge_voltage'],
            settings['max_discharge_current'],
            settings['batt_capacity'],
            settings['DCDC_output_mode'])
        query = f"""
        INSERT INTO sensor_metadata (
                             id,
                             ip_address,
                             sysname,
                             location,
                             batt_type,
                             charge_voltage,
                             charge_current,
                             float_voltage,
                             low_voltage,
                             deep_discharge_voltage,
                             max_discharge_current,
                             batt_capacity,
                             DCDC_output_mode
                             ) 
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE
        SET
        ip_address = %s,
        sysname = %s,
        location = %s,
        batt_type = %s,
        charge_voltage = %s,
        charge_current = %s,
        float_voltage = %s,
        low_voltage = %s,
        deep_discharge_voltage = %s,
        max_discharge_current = %s,
        batt_capacity = %s,
        DCDC_output_mode = %s;
        """
        return self.cursor.execute(query, values)
    
    def insert_metrics(self, metrics):
        values = (
            metrics["unix_timestamp"],
            metrics["device_id"],
            metrics["input_voltage_min"],
            metrics["input_voltage_avg"],
            metrics["input_voltage_max"],
            metrics["input_current_min"],
            metrics["input_current_avg"],
            metrics["input_current_max"],
            metrics["output_voltage_min"],
            metrics["output_voltage_avg"],
            metrics["output_voltage_max"],
            metrics["output_current_min"],
            metrics["output_current_avg"],
            metrics["output_current_max"],
            metrics["batt_voltage_min"],
            metrics["batt_voltage_avg"],
            metrics["batt_voltage_max"],
            metrics["batt_current_min"],
            metrics["batt_current_avg"],
            metrics["batt_current_max"],
            metrics["batt_int_resistance"],
            metrics["batt_charge_capacity"],
            metrics["operating_time"],
            metrics["batt_operating_time"])
        query = f"""
        INSERT INTO sensor_data (
            time,
            sensor_id,
            input_voltage_min,
            input_voltage_avg,
            input_voltage_max,
            input_current_min,
            input_current_avg,
            input_current_max,
            output_voltage_min,
            output_voltage_avg,
            output_voltage_max,
            output_current_min,
            output_current_avg,
            output_current_max,
            batt_voltage_min,
            batt_voltage_avg,
            batt_voltage_max,
            batt_current_min,
            batt_current_avg,
            batt_current_max,
            batt_int_resistance,
            batt_charge_capacity,
            operating_time,
            batt_operating_time
        )
        VALUES(to_timestamp(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """
        
        return self.cursor.execute(query, values)

    def close_connection(self):
        self.conn.commit()
        self.cursor.close()

def init_connection(config):
    host = config.db_host
    port = config.db_port
    db_password = config.db_password
    db_username = config.db_username
    db_name = config.db_name
    #print(config)
    
    try:
        CONNECTION = f"postgres://{db_username}:{db_password}@{host}:{port}/{db_name}"
        return psycopg.connect(CONNECTION)
        
    except:
        return ("!!Error connecting to the database")

def main():
    from config import CONFIG
    config = CONFIG()
    db = DB(init_connection(config))
    db.create_tables()
    db.initialize_device(config)
    db.close_connection()

if __name__ == "__main__":
    main()
