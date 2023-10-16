import psycopg2
import os

class DB:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = self.conn.cursor()

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
                location VARCHAR(50)
            );
            """
        check_exists_sensor_hypertable = """
            SELECT EXISTS (
                SELECT 1
                FROM _timescaledb_catalog.hypertable
                WHERE table_name = 'sensor_data'
            )
            """
        create_sensor_hypertable = """
            CREATE TABLE sensor_data (
                time TIMESTAMPTZ NOT NULL,
                sensor_id INTEGER

            )"""
        self.cursor.execute(check_exists_sensors)
        if self.cursor.fetchone()[0]:
            print("sensors table exists already")
        else:
            self.cursor.execute(create_sensors_table)
            print("created sensors table")
        self.cursor.execute(check_exists_sensor_hypertable)
        
        
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
   db = DB(init_connection())
   print(db.create_tables())
   db.close_connection()

if __name__ == "__main__":
    main()
