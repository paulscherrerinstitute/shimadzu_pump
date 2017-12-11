import logging
from argparse import ArgumentParser

import sys

from pcaspy import SimpleServer
from shimadzu_pump import ioc


def main(pump_host, ioc_prefix, pump_polling_interval):
    _logger = logging.getLogger(ioc_prefix)
    _logger.info("Starting ioc with prefix '%s', pump polling interval '%s', and pump_host '%s'.",
                 ioc_prefix, pump_polling_interval, pump_host)

    server = SimpleServer()
    server.createPV(prefix=ioc_prefix, pvdb=ioc.pvdb)
    driver = ioc.SchimadzuDriver(pump_host=pump_host, pump_polling_interval=pump_polling_interval)

    try:

        while True:
            server.process(0.1)

    except KeyboardInterrupt:
        _logger.info("User requested ioc termination. Exiting.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("ioc_prefix", type=str, help="Prefix of the IOC.")
    parser.add_argument("pump_host", type=str, help="Pump host.")
    parser.add_argument("--polling_interval", default=1, type=float, help="Pump polling interval.")
    parser.add_argument("--log_level", default="WARNING",
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help="Log level to use.")

    arguments = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=arguments.log_level)

    main(ioc_prefix=arguments.ioc_prefix,
         pump_host=arguments.pump_host,
         pump_polling_interval=arguments.polling_interval)
