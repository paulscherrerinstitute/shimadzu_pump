import logging
from argparse import ArgumentParser

import sys

from tests.utils import start_test_ioc


def main():
    parser = ArgumentParser()
    parser.add_argument("ioc_prefix", type=str, help="Prefix of the IOC.")
    parser.add_argument("--polling_interval", default=1, type=float, help="Pump polling interval.")
    parser.add_argument("--log_level", default="WARNING",
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help="Log level to use.")

    arguments = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=arguments.log_level)

    start_test_ioc(arguments.ioc_prefix, arguments.polling_interval)


if __name__ == "__main__":
    main()
