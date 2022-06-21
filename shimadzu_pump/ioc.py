from threading import Thread
from time import sleep

from pcaspy import Driver
import logging
from requests import exceptions

_logger = logging.getLogger("ShimadzuDriver")

valve_dict = { 
"both_0": 0,
"first_1": 1,
"second_1": 2,
"both_1": 12
}

pvdb = {
    "PUMPING": {
        "type": "enum",
        'enums': ['OFF', 'ON']
    },

    # This is a special case - do not include it in write_pvname_to_shimadzu_property.
    "PUMPING_SP": {
        "type": "enum",
        'enums': ['OFF', 'ON']
    },

    "FLOW": {
        "type": "float",
        "prec": 4
    },

    "FLOW_SP": {
        "type": "float",
        "prec": 4
    },

    "PRESSURE": {
        "type": "float",
        "prec": 4
    },

    "PRESSURE_MIN": {
        "type": "float",
        "prec": 4
    },

    "PRESSURE_MIN_SP": {
        "type": "float",
        "prec": 4
    },

    "PRESSURE_MAX": {
        "type": "float",
        "prec": 4
    },

    "PRESSURE_MAX_SP": {
        "type": "float",
        "prec": 4
    },

#TODO: if this is not implemented in UI- let's make this an ENUM with valve states, needs to be implemented in code
# Valve A | Valve B  | Event val 
#    0          0	0
#    1          0	1
#    0          1	2
#    1          1	12
#    "VALVE_STATE": {
#        "type": "enum",
#        'enums': ["both_0", "first_1", "second_1", "both_1"]
#    },

    "EVENT": {
        "type": "int"
    },

    "EVENT_SET": {
        "type": "int"
    },
   #special case - do not include in poll parameters
#TODO: make this a sequence
    "CLEAR_ERROR": {
        "type": "enum",
        'enums': ['Do not clear','Clear']
    },

    "PRESSURE_UNIT": {
        "type": "enum",
#OLD        'enums': ['MPa','kgf/cm2','psi','bar']
        'enums': ['kgf/cm2','psi','MPa','bar']
    },

    "PRESSURE_UNIT_SET": {
        "type": "enum",
#OLD        'enums': ['MPa','kgf/cm2','psi','bar']
        'enums': ['kgf/cm2','psi','MPa','bar']
    },

    "HOSTNAME": {
        "type": "string"
    }
}

# Pump hostname PV
hostname_PV = "HOSTNAME"

# PV name : Pump property name
write_pvname_to_shimadzu_property = {
    "FLOW_SP": "flow",
    "PRESSURE_MIN_SP": "min_pressure",
    "PRESSURE_MAX_SP": "max_pressure",
    "EVENT_SET": "event",
    "CLEAR_ERROR": "clear_error",
    "PRESSURE_UNIT_SET": "pressure_unit"
}

# Pump property name : PV name
properties_to_poll = {
    "flow": "FLOW",
    "pressure": "PRESSURE",
    "min_pressure": "PRESSURE_MIN",
    "max_pressure": "PRESSURE_MAX",
    "pumping": "PUMPING",
    "event": "EVENT",
    "pressure_unit": "PRESSURE_UNIT"
}


class EpicsShimadzuPumpDriver(Driver):

    def __init__(self, communication_driver, pump_polling_interval, hostname):
        connectionError = True # Also set when pump is not connected
        Driver.__init__(self)
        _logger.info("Starting epics driver with polling interval '%s' seconds.", pump_polling_interval)

        super().setParam(hostname_PV, hostname)

        self.communication_driver = communication_driver
        self.pump_polling_interval = pump_polling_interval
        # Start login thread.
        self.login_thread = Thread(target=self.try_connect)
        self.login_thread.setDaemon(True)
        self.login_thread.start()
        # Start the polling and connection check thread.
        self.polling_thread = Thread(target=self.poll_pump)
        self.polling_thread.setDaemon(True)
        self.polling_thread.start()

    # Login to the pump, sleep and retry if not connected.
    def try_connect():
        while(connectionError):
            try:
                self.communication_driver.login()
                connectionError=False
            except exceptions.ConnectionError:
                _logger.warning("Error connecting to pump, will retry in 30 seconds.")
                connectionError=True
        sleep(30)

    def poll_pump(self):

        while True:

            try:
                # Poll pump, sleep and retry if not connected.
                # However if pump was turned off and back on, we need to log back in first via the other thread.
                if (not connectionError):
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
                
            except exceptions.ConnectionError:
               _logger.warning("Error connecting to pump, will retry in 15s + poll interval.")
               connectionError = True
               sleep(15)

            except:
                _logger.exception("Connected but could not read pump properties.")
                connectionError = True

            server.process(0.1)
            sleep(self.pump_polling_interval)

    def write(self, reason, value):

        # The PV is a pump parameter.
        if reason in write_pvname_to_shimadzu_property:

            pump_value_name = write_pvname_to_shimadzu_property[reason]

            try:

                _logger.info("Setting pump property '%s' to values '%s'.", pump_value_name, value)

                self.communication_driver.set(pump_value_name, value)

                super().setParam(reason, value)
                # If PV was the error reset request, reset it.
                if reason == "CLEAR_ERROR":
                  super().setParam(reason, "Do not clear")
                   
                self.updatePVs()

            except:
                _logger.exception("Could not set pump property '%s' to value '%s'.", pump_value_name, value)

        # The PV is a START/STOP PV.
        if reason == "PUMPING_SP":

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

         # The PV is the pump hostname.
        if reason == "HOSTNAME":
            super().setParam(reason, value)
            self.updatePVs()

