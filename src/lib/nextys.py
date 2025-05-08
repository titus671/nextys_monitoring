import minimalmodbus
import time


class NEXTYS:
    def __init__(self, config):
        self.config = config

        try:
            self.instrument = minimalmodbus.Instrument(config.usb_address, config.slave_address)
        except FileNotFoundError as e:
            print(f"error in NEXTYS(): {e}")
        self.device_id = config.device_id

    def read_settings(self):

        return {
            "device_id": self.device_id,
            "ip_address": self.config.ip_address,
            "sysName": self.config.sysName,
            "location": self.config.location,
            "batt_type": self.get_batt_type(),
            "charge_voltage": self.get_charge_voltage(),
            "charge_current": self.get_charge_current(),
            "float_voltage": self.get_float_voltage_setting(),
            "low_voltage": self.get_low_voltage_setting(),
            "deep_discharge_voltage": self.get_deep_discharge_voltage_setting(),
            "max_discharge_current": self.get_max_discharge_current_setting(),
            "batt_capacity": self.get_batt_capacity_setting(),
            "DCDC_output_mode": self.get_DCDC_output_mode()
        }

    def read_meters(self):
        try:
            return {
                "unix_timestamp": time.time(),
                "device_id": self.device_id,
                "input_voltage": self.get_input_voltage(),
                "input_current": self.get_input_current(),
                "output_voltage": self.get_output_voltage(),
                "output_current": self.get_output_current(),
                "batt_voltage": self.get_batt_voltage(),
                "batt_current": self.get_batt_current(),
                "batt_int_resistance": self.get_batt_int_resistance(),
                "batt_charge_capacity": self.get_batt_charge_capacity(),
                "operating_time": self.get_operating_time(),
                "batt_operating_time": self.get_batt_operating_time()
            }
        except Exception as e:
            print("Error reading values")
            raise e

    #
    # The below funcions contain the
    # currently implemented setting registers

    def set_batt_type(self):
        ...

    def get_batt_type(self):
        return self.instrument.read_register(0x1010, 0)

    def set_charge_voltage(self):
        ...

    def get_charge_voltage(self):
        return self.instrument.read_register(0x1011, 1)

    def set_charge_current_setting(self):
        ...

    def get_charge_current(self):
        return self.instrument.read_register(0x1012, 1)

    def set_float_voltage(self):
        ...

    def get_float_voltage_setting(self):
        return self.instrument.read_register(0x1013, 1)

    def set_low_voltage(self):
        ...

    def get_low_voltage_setting(self):
        return self.instrument.read_register(0x1014, 1)

    def set_deep_discharge_voltage(self):
        ...

    def get_deep_discharge_voltage_setting(self):
        return self.instrument.read_register(0x1015, 1)

    def set_max_discharge_current(self):
        ...

    def get_max_discharge_current_setting(self):
        return self.instrument.read_register(0x1016, 1)

    def set_batt_capacity(self):
        ...

    def get_batt_capacity_setting(self):
        return self.instrument.read_register(0x1017, 1)

    def set_DCDC_output_mode(self):
        ...

    def get_DCDC_output_mode(self):
        return self.instrument.read_register(0x102A, 0)

    #
    # Below are the implemented
    # measurements

    def get_input_voltage(self):
        return self.instrument.read_register(0x2000, 1, signed=True)

    def get_input_current(self):
        return self.instrument.read_register(0x2001, 1, signed=True)

    def get_output_voltage(self):
        return self.instrument.read_register(0x2002, 1, signed=True)

    def get_output_current(self):
        return self.instrument.read_register(0x2003, 1, signed=True)

    def get_batt_voltage(self):
        return self.instrument.read_register(0x2004, 1, signed=True)

    def get_batt_current(self):
        return self.instrument.read_register(0x2005, 1, signed=True)

    def get_batt_int_resistance(self):
        return self.instrument.read_register(0x2009, 1, signed=True)

    def get_batt_charge_capacity(self):
        return self.instrument.read_register(0x200B, 1, signed=True)

    def get_operating_time(self):
        return self.instrument.read_long(0x2020)

    def get_batt_operating_time(self):
        return self.instrument.read_long(0x2022)


def main():
    import json
    from config import CONFIG
    nexty = NEXTYS(CONFIG())
    r = nexty.read_settings()
    print(json.dumps(r, indent=2))
    m = nexty.read_meters()
    print(json.dumps(m, indent=2))


if __name__ == "__main__":
    main()
