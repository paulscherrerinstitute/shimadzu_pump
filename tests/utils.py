import logging

from pcaspy import SimpleServer

from shimadzu_pump.ioc import pvdb, EpicsShimadzuPumpDriver

_logger = logging.getLogger(__name__)

class MockShimadzuCbm20(object):
    def __init__(self):
        self.data = {"flow": 0,
                     "max_pressure": 100,
                     "min_pressure": 0,
                     "pumping": 0}

    def login(self, user="Admin", password="Admin"):
        return "session_id"

    def logout(self):
        return

    def start(self):
        self.data["pumping"] = 1

    def stop(self):
        self.data["pumping"] = 0

    def set(self, name, value):
        self.data[name] = value

    def get(self, name):
        return self.data[name]

    def get_all(self):
        return self.data


def start_test_ioc(ioc_prefix, polling_interval):

    _logger.info("Starting test IOC with prefix '%s' and polling_interval '%s'.", ioc_prefix, polling_interval)

    server = SimpleServer()
    server.createPV(prefix=ioc_prefix, pvdb=pvdb)

    _logger.info("Available PVs:\n%s", [ioc_prefix + pv for pv in pvdb.keys()])

    communication_driver = MockShimadzuCbm20()
    driver = EpicsShimadzuPumpDriver(communication_driver=communication_driver,
                                     pump_polling_interval=polling_interval)

    try:

        while True:
            server.process(0.1)

    except KeyboardInterrupt:
        _logger.info("User terminated execution.")
