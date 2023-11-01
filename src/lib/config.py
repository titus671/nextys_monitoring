import json
import os

class CONFIG:
    def __init__(self):
        self.cwd = os.getcwd()
        with open(os.path.join(self.cwd, "modbus_setting_registers.json")) as registers:
            self.setting_registers = json.load(registers)
        with open(os.path.join(self.cwd, "modbus_metering_registers.json")) as m_registers:
            self.metering_registers = json.load(m_registers)
        with open(os.path.join(self.cwd, "config.json")) as config:
            self.config = json.load(config)
            self.usb_address = self.config["usb_address"]
            self.slave_address = self.config["slave_address"]
            self.device_id = self.config.get("device_id", None)
            self.ip_address = self.config["ip_address"]
            self.sysName = self.config["sysName"]
            self.location = self.config["location"]
            self.db_host = self.config.get("db_host", "localhost")
            self.db_port = self.config.get("db_port", 5432)
            self.db_username = self.config.get("db_username", "postgres")
            self.db_password = self.config.get("db_password", "password")
            self.db_name = self.config.get("db_name", "postgres")
        

    def set_device_id(self, id):
        self.config["device_id"] = id
        with open(os.path.join(self.cwd, "config.json"), 'w') as c:
           json.dump(self.config, c, indent=4) 

def main():
    config = CONFIG()
    print(config.config)
    #print(config.setting_registers["battery_type"])
if __name__ == "__main__":
    main()
