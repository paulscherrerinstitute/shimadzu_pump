import logging
from argparse import ArgumentParser

import sys

from pcaspy import SimpleServer
from shimadzu_pump import ioc
from shimadzu_pump.shimadzu_driver import ShimadzuCbm20


def main():
    parser = ArgumentParser()
    parser.add_argument("ioc_prefix", type=str, help="Prefix of the IOC, include seperator.")
    parser.add_argument("pump_host", type=str, help="Pump host.")
    parser.add_argument("--polling_interval", default=1, type=float, help="Pump polling interval.")
    parser.add_argument("--log_level", default="WARNING",
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help="Log level to use.")

    arguments = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=arguments.log_level)

    _logger = logging.getLogger(arguments.ioc_prefix)
    _logger.info("Starting ioc with prefix '%s', pump polling interval '%s' seconds, and pump_host '%s'.",
                 arguments.ioc_prefix, arguments.polling_interval, arguments.pump_host)

    server = SimpleServer()
    server.createPV(prefix=arguments.ioc_prefix, pvdb=ioc.pvdb)

    communication_driver = ShimadzuCbm20(host=arguments.pump_host)
    driver = ioc.EpicsShimadzuPumpDriver(communication_driver=communication_driver,
                                         pump_polling_interval=arguments.polling_interval)

    try:

        while True:
            server.process(0.1)

    except KeyboardInterrupt:
        _logger.info("User requested ioc termination. Exiting.")


if __name__ == "__main__":
    main()
