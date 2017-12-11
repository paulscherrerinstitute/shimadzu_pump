from threading import Thread
from time import sleep

from pcaspy import Driver
import logging
from shimadzu_pump.shimadzu_driver import ShimadzuCbm20

_logger = logging.getLogger("SchimadzuDriver")

pvdb = {
    "FLOW": {
        "type": "float",
        "prec": 4
    },

    "FLOW-SET": {
        "type": "float",
        "prec": 4
    },

    "PUMPING": {
        "type": "str"
    },

    # This is a special case - do not include it in write_pvname_to_schimatzu_property.
    "PUMPING-SET": {
        "type": "int"
    },

    "PRESSURE": {
        "type": "float",
        "prec": 4
    },
}

write_pvname_to_schimatzu_property = {
    "FLOW-SET": "Flow"
}

# Pump property name : PV name
properties_to_poll = {
    "Flow": "FLOW",
    "Pressure": "PRESSURE",
    "Pumping": "PUMPING"
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

                pump_data = self.communication_driver.get_all()

                for pump_property, pv_name in properties_to_poll.items():

                    _logger.debug("Reading pump property '%s'.", pump_property)

                    if pump_property not in pump_data:
                        _logger.warning("Pump property '%s' not in received pump data: %s", pump_property, pump_data)
                        continue

                    value = pump_data[pump_property]

                    _logger.debug("Pump property '%s'='%s'", pump_property, value)

                    super().setParam(pv_name, value)

                self.updatePVs()

            except:
                _logger.exception("Could not read pump properties.")

            sleep(self.pump_polling_interval)

    def write(self, reason, value):

        # The PV is a pump parameter.
        if reason in write_pvname_to_schimatzu_property:

            pump_value_name = write_pvname_to_schimatzu_property[reason]

            try:

                _logger.info("Setting pump property '%s' to values '%s'.", pump_value_name, value)

                self.communication_driver.set(pump_value_name, value)

                super().setParam(reason, value)
                self.updatePVs()

            except:
                _logger.exception("Could not set pump property '%s' to value '%s'.", pump_value_name, value)

        # The PV is a START/STOP PV.
        if reason == "PUMPING-SET":

            try:

                if value:
                    _logger.info("Starting the pump.")
                    self.communication_driver.start()

                else:
                    _logger.info("Stopping the pump.")
                    self.communication_driver.stop()

                super().setParam(reason, value)
                self.updatePVs()

            except:
                _logger.exception("Cannot change the pump status ON to '%s'.", value)
