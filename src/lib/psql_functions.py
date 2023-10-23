import psycopg2
import os, sys

class DB:
    def __init__(self, conn):
        from lib.logger import Logger
        self.logger = Logger()
        try:
            self.conn = conn
            self.cursor = self.conn.cursor()
        except AttributeError:
            self.logger.log("Connection was not valid,\nconsider double checking your creds")
            sys.exit(1)

    def create_tables(self):
        check_exists_sensors = """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'sensors'
            )"""
        create_sensors_table = """
            CREATE TABLE sensors (
                id SERIAL PRIMARY KEY,
                ip_address INET,
                sysName VARCHAR(50),
                location VARCHAR(50),
                batt_type INTEGER,
                charge_voltage DOUBLE PRECISION,
                charge_current DOUBLE PRECISION,
                float_voltage DOUBLE PRECISION,
                low_voltage DOUBLE PRECISION,
                deep_discharge_voltage DOUBLE PRECISION,
                max_discharge_current DOUBLE PRECISION,
                batt_capacity DOUBLE PRECISION,
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
                input_voltage DOUBLE PRECISION,
                input_current DOUBLE PRECISION,
                output_voltage DOUBLE PRECISION,
                output_current DOUBLE PRECISION,
                batt_voltage DOUBLE PRECISION,
                batt_current DOUBLE PRECISION,
                batt_int_resistance DOUBLE PRECISION,
                batt_charge_capacity DOUBLE PRECISION,
                operating_time INTEGER,
                batt_operating_time INTEGER,
                FOREIGN KEY (sensor_id) REFERENCES sensors (id)
            );"""
        create_sensor_data_hypertable = """
            SELECT create_hypertable('sensor_data', 'time');
            """
        self.cursor.execute(check_exists_sensors)
        if self.cursor.fetchone()[0]:
            self.logger.log("sensors table exists already")
        else:
            self.cursor.execute(create_sensors_table)
            self.logger.log("created sensors table")
        self.cursor.execute(check_exists_sensor_hypertable)
        if self.cursor.fetchone()[0]:
            self.logger.log("sensor_data hypertable exists already")
        else:
            self.cursor.execute(create_sensor_data_table)
            self.logger.log("created sensor_data table")
            self.cursor.execute(create_sensor_data_hypertable)
            self.logger.log("created sensor_data hypertable")

    def initialize_device(self, config):
        values = (
            f"{config.ip_address}",
            f"{config.sysName}",
            f"{config.location}"
        )
        query = f"""
        INSERT INTO sensors (
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
 
    def insert_settings(self, settings: dict):
        id = settings["device_id"]
        ip_address = settings["ip_address"]
        sysName = settings["sysName"]
        location = settings["location"]
        values = (
            f"{id}",
            f"{ip_address}",
            f"{sysName}",
            f"{location}",
            settings['batt_type'],
            settings['charge_voltage'],
            settings['charge_current'],
            settings['float_voltage'],
            settings['low_voltage'],
            settings['deep_discharge_voltage'],
            settings['max_discharge_current'],
            settings['batt_capacity'],
            settings['DCDC_output_mode'],
            f"{ip_address}",
            f"{sysName}",
            f"{location}",
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
        INSERT INTO sensors (
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
        
    def close_connection(self):
        self.conn.commit()
        self.cursor.close()

def init_connection():
    host = os.environ.get("PSQL_HOST", "localhost")
    port = os.environ.get("PSQL_PORT", "5432")
    db_password = os.environ.get("PSQL_PASSWORD", "password")
    db_username = os.environ.get("PSQL_USERNAME", "postgres")
    db_name = os.environ.get("DB_NAME", "postgres")
    
    try:
        CONNECTION = f"postgres://{db_username}:{db_password}@{host}:{port}/{db_name}"
        return psycopg2.connect(CONNECTION)
        
    except:
        return ("!!Error connecting to the database")

def main():
    from config import CONFIG
    db = DB(init_connection())
    db.create_tables()
    db.initialize_device(CONFIG())
    db.close_connection()

if __name__ == "__main__":
    main()
