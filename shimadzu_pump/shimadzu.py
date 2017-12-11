import logging

import requests
from xml.etree import ElementTree

headers = {'Content-Type': 'text'}

request_data = {
    "login": "<Login><Mode>0</Mode><Certification><UserID>%s</UserID><Password>%s</Password>"
             "<SessionID/><Result/></Certification></Login>",
    "logout": "<Login><Mode>-1</Mode></Login>",
    "start": "<Event><Method><PumpBT>1</PumpBT></Method></Event>",
    "stop": "<Event><Method><PumpBT>0</PumpBT></Method></Event>",
    "get": "<Method><No>0</No><Pumps></Pumps></Method>",
    "set": "<Method><No>0</No><Pumps><Pump><UnitID>A</UnitID><Usual><%(name)s>%(value).4f</%(name)s></Usual>"
           "</Pump></Pumps></Method>"}

parameters = {"Flow": ("Pumps/Pump/Usual/Flow", float),
              "Pressure": ("Pumps/Pump/Usual/Tpress", float)}

_logger = logging.getLogger(__name__)


def extract_element(parameter_properties, response):

    _logger.debug("Trying to extract '%s' from response: %s", parameter_properties, response)

    parameter_path = parameter_properties[0]
    parameter_type = parameter_properties[1]

    tree = ElementTree.fromstring(response)
    string_value = tree.find(parameter_path).text

    return parameter_type(string_value)


class ShimadzuCbm20(object):

    def __init__(self, host):

        self.host = host

        _logger.debug("Starting ShimadzuCbm20 driver with exposed parameters: %s", parameters)

        self.endpoints = {"login": "http://%s/cgi-bin/Login.cgi" % self.host,
                          "event": "http://%s/cgi-bin/Event.cgi" % self.host,
                          "method": "http://%s/cgi-bin/Method.cgi" % self.host}

    def login(self, user="Admin", password="Admin"):

        _logger.info("Trying to log in as '%s'.", user)

        login_data = request_data["login"] % (user, password)

        response_text = requests.get(self.endpoints["login"], data=login_data, headers=headers).text

        _logger.debug("Response from pump: %s", response_text)

        session_id = extract_element("Certification/SessionID", response_text)

        _logger.debug("Received session_id='%s'.", session_id)

        if not session_id:
            raise ValueError("You are already logged in. Please logout first.")

        return session_id

    def logout(self):

        _logger.info("Logging out.")

        logout_data = request_data["logout"]
        response_text = requests.get(self.endpoints["login"], data=logout_data, headers=headers).text

        _logger.debug("Response from pump: %s", response_text)

    def start(self):

        _logger.info("Starting pump.")

        start_data = request_data["start"]
        response_text = requests.get(self.endpoints["event"], data=start_data, headers=headers).text

        _logger.debug("Response from pump: %s", response_text)

    def stop(self):

        _logger.info("Stopping pump.")

        stop_data = request_data["stop"]
        response_text = requests.get(self.endpoints["event"], data=stop_data, headers=headers).text

        _logger.debug("Response from pump: %s", response_text)

    def set(self, name, value):

        _logger.debug("Setting parameter '%s'='%s'.", name, value)

        if name not in parameters:
            raise ValueError(
                "Parameter name '%s' not recognized. Available parameters: %s" % (name, list(parameters.keys())))

        set_flow_data = request_data["set"] % {"name": name, "value": value}
        response_text = requests.get(self.endpoints["method"], data=set_flow_data, headers=headers).text

        _logger.debug("Response from pump: %s", response_text)

        return extract_element(parameters[name], response_text)

    def get(self, name):

        if name not in parameters:
            raise ValueError(
                "Parameter name '%s' not recognized. Available parameters: %s" % (name, list(parameters.keys())))

        get_data = request_data["get"]
        response_text = requests.get(self.endpoints['method'], data=get_data, headers=headers).text

        return extract_element(parameters[name], response_text)

    def get_all(self):

        get_data = request_data["get"]
        response_text = requests.get(self.endpoints['method'], data=get_data, headers=headers).text

        data = {}

        for parameter_name, parameter_properties in parameters.items():
            data[parameter_name] = extract_element(parameter_properties, response_text)

        return data
