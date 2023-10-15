import json

class CONFIG:
    def __init__(self):
        
        with open("modbus_setting_registers.json") as registers:
            self.setting_registers = json.load(registers)
        with open("modbus_metering_registers.json") as m_registers:
            self.metering_registers = json.load(m_registers)
        with open("config.json") as config:
            c = json.load(config)
            self.usb_address = c["usb_address"]
            self.slave_address = c["slave_address"]

def main():
    config = CONFIG()
    print(config.setting_registers["battery_type"])
if __name__ == "__main__":
    main()
