from pcaspy import Driver
import logging
from shimadzu_pump.schimadzu import ShimadzuCbm20

_logger = logging.getLogger("SchimadzuDriver")

pvdb = {
    "FLOW": {
        "type": "float",
        "prec": 4,
        "scan": 1
    },

    "FLOW-SET": {
        "type": "float",
        "prec": 4
    }
}

write_pvname_to_schimatzu_property = {
    "FLOW-SET": "Flow"
}

read_pvname_to_schimatzu_property = {
    "FLOW": "Flow"
}


class SchimadzuDriver(Driver):

    def __init__(self, pump_host):
        Driver.__init__(self)
        _logger.info("Starting communication driver with pump_host '%s'.", pump_host)

        self.communication_driver = ShimadzuCbm20(pump_host)

    def write(self, reason, value):

        # The PV is a pump parameter.
        if reason in write_pvname_to_schimatzu_property:

            # Write the value to the pump.
            pump_value_name = write_pvname_to_schimatzu_property[reason]
            self.communication_driver.set(pump_value_name, value)

        return super().setParam(reason, value)

    def read(self, reason):

        # The PV is a pump parameter.
        if reason in read_pvname_to_schimatzu_property:

            # Read the value from the pump.
            pump_value_name = read_pvname_to_schimatzu_property[reason]
            value = self.communication_driver.get(pump_value_name)

            self.setParam(reason, value)

        return super().getParam(reason)
