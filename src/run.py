from lib.nextys import NEXTYS
from lib.config import CONFIG
from lib.psql_functions import DB, init_connection

def main():
    config = CONFIG()
    nexty = NEXTYS(config)
    settings = nexty.read_settings()
    measurements = nexty.read_meters()
    db = DB(init_connection())
    db.initialize_device(config)
    db.insert_settings(settings)
    db.close_connection()

if __name__ == "__main__":
    main()

