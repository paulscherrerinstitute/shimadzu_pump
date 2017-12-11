from threading import Thread
from time import sleep

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

    def __init__(self, pump_host, pump_polling_interval):
        Driver.__init__(self)
        _logger.info("Starting communication driver with pump_host '%s' and polling interval '%s'.",
                     pump_host, pump_polling_interval)

        self.pump_polling_interval = pump_polling_interval

        self.communication_driver = ShimadzuCbm20(pump_host)

        # Start the polling thread.
        self.polling_thread = Thread(target=self.poll_pump)
        self.polling_thread.setDaemon(True)
        self.polling_thread.start()

    def poll_pump(self):

        while True:

            try:

                for pv_name, pump_property in read_pvname_to_schimatzu_property.items():

                    _logger.debug("Reading pump property '%s'.", pump_property)
                    value = self.communication_driver.get(pump_property)
                    _logger.debug("Pump property '%s'='%s'", pump_property, value)

                    self.setParam(pv_name, value)

                self.updatePVs()

            except:
                _logger.exception("Could not read pump properties.")

            sleep(self.polling_interval)

    def write(self, reason, value):

        # The PV is a pump parameter.
        if reason in write_pvname_to_schimatzu_property:

            pump_value_name = write_pvname_to_schimatzu_property[reason]

            _logger.info("Setting pump property '%s' to values '%s'.", pump_value_name, value)

            self.communication_driver.set(pump_value_name, value)

        return super().setParam(reason, value)
