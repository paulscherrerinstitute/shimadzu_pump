import logging

import requests
from xml.etree import ElementTree

_logger = logging.getLogger(__name__)

get_parameters = {"flow": ("method", "get_method", "Pumps/Pump/Usual/Flow", float),
                  "max_pressure": ("method", "get_method", "Pumps/Pump/Usual/Pmax", float),
                  "min_pressure": ("method", "get_method", "Pumps/Pump/Detail/Pmin", float),
                  "pressure": ("sysmon", "get_sysmon", "SysMon/Method/Pumps/Pump/Press", float),
                  "pressure_unit": ("config", "get_config", "Env/Pumps/Pump/PressUnit", int),
                  "event":   ("method", "get_method", "Ctrl/Usual/Eventset", int),
                  "pumping": ("monitor", "get_monitor", "Config/Situation/Pumps/Pump/OpState", int),
                  #Error is special, don't include in 'get_all'
                  "clear_error": ("event", "get_event", "Error/Clear", int)
}

set_parameters = {"flow": ("method", "set_pump_usual", "Flow"),
                  "min_pressure": ("method", "set_pump_detail", "Pmin"),
                  "max_pressure": ("method", "set_pump_usual", "Pmax"),
                  "event": ("method", "set_ctrl_usual", "Eventset"),
                  "clear_error": ("event", "set_event_error", "Clear"),
                  "pressure_unit": ("config", "set_config", "PressUnit")
}

header_data = {'Content-Type': 'text'}

request_data = {
    "login": "<Login><Mode>0</Mode><Certification><UserID>%s</UserID><Password>%s</Password>"
             "<SessionID/><Result/></Certification></Login>",
    "logout":"<Login><Mode>-1</Mode></Login>",
    "start": "<Event><Method><PumpBT>1</PumpBT></Method></Event>",
    "stop": "<Event><Method><PumpBT>0</PumpBT></Method></Event>",
    "get_method":  "<Method><No>0</No><Pumps></Pumps><Ctrl></Ctrl></Method>",
    "get_monitor": "<Monitor><Config><Situation><Pumps></Pumps></Situation></Config></Monitor>",
    "get_sysmon": "<Monitor><SysMon><Method><Pumps><Pump><UnitID>A</UnitID></Pump></Pumps></Method></SysMon></Monitor>",
    "get_config": "<Config><Env><Pumps></Pumps></Env></Config>",
    "get_event": "<Event></Event>",
    "set_pump_usual": "<Method><No>0</No><Pumps><Pump><UnitID>A</UnitID><Usual><%(name)s>%(value).4f</%(name)s></Usual>"
                 "</Pump></Pumps></Method>",
    "set_pump_detail": "<Method><No>0</No><Pumps><Pump><UnitID>A</UnitID><Detail><%(name)s>%(value).4f</%(name)s></Detail>"
                 "</Pump></Pumps></Method>",
    "set_ctrl_usual": "<Method><No>0</No><Ctrl><Usual><%(name)s>%(value)d</%(name)s></Usual></Ctrl></Method>",
    "set_event_error": "<Event><Error><%(name)s>%(value)d</%(name)s></Error></Event>",
    "set_config": "<Config><Env><Pumps><Pump><UnitID>A</UnitID><%(name)s>%(value)d</%(name)s></Pump></Pumps></Env></Config>"
}


def extract_element(parameter_properties, response):
    _logger.debug("Trying to extract '%s' from response: %s", parameter_properties, response)

    parameter_path = parameter_properties[2]
    parameter_converter = parameter_properties[3]

    tree = ElementTree.fromstring(response)
    string_value = tree.find(parameter_path).text

    return parameter_converter(string_value)


class ShimadzuCbm20(object):
    def __init__(self, host):

        self.host = host

        _logger.info("Starting ShimadzuCbm20 communication driver with host='%s'", self.host)

        self.endpoints = {"login": "http://%s/cgi-bin/Login.cgi" % self.host,
                          "event": "http://%s/cgi-bin/Event.cgi" % self.host,
                          "method": "http://%s/cgi-bin/Method.cgi" % self.host,
                          "monitor": "http://%s/cgi-bin/Monitor.cgi" % self.host,
                          "config": "http://%s/cgi-bin/Config.cgi" % self.host,
                          "sysmon": "http://%s/cgi-bin/SysMon.cgi" % self.host}

    def login(self, user="Admin", password="Admin"):

        try:
            self.logout()
    
            _logger.info("Attempting to login as '%s'.", user)
    
            login_data = request_data["login"] % (user, password)
    
            response_text = requests.get(self.endpoints["login"], data=login_data, headers=header_data).text
            _logger.debug("Response from pump: %s", response_text)
    
            session_id = extract_element((None, None, "Certification/SessionID", str), response_text)
            _logger.debug("Received session_id='%s'.", session_id)
    
            if not session_id:
                raise ValueError("You are already logged in. Please logout first.")
    
            _logger.info("Logging in as '%s' was successful.", user)
    
            return session_id
         
        except:
            raise


    def logout(self):

        try:
            _logger.info("Attempting logout.")

            logout_data = request_data["logout"]
            response_text = requests.get(self.endpoints["login"], data=logout_data, headers=header_data).text

            _logger.debug("Response from pump: %s", response_text)

        except:
            raise

    def start(self):

        try:
            _logger.info("Starting pump.")

            start_request_data = request_data["start"]

            response_text = requests.get(self.endpoints["event"], data=start_request_data, headers=header_data).text
            _logger.debug("Response from pump: %s", response_text)
        
        except:
            raise
    
    def stop(self):

        try:
            _logger.info("Stopping pump.")

            stop_request_data = request_data["stop"]

            response_text = requests.get(self.endpoints["event"], data=stop_request_data, headers=header_data).text
            _logger.debug("Response from pump: %s", response_text)
        
        except:
            raise

    def _get_request_data(self, name, parameters):
        if name not in parameters:
            raise ValueError(
                "Parameter name '%s' not recognized. Available parameters: %s" % (
                    name, list(parameters.keys())))

        parameter_properties = parameters[name]

        endpoint_name = parameter_properties[0]
        if endpoint_name not in self.endpoints:
            raise ValueError("Parameter '%s' specified endpoint name '%s' that does not exist." %
                             (name, endpoint_name))

        request_data_name = parameter_properties[1]
        if request_data_name not in request_data:
            raise ValueError("Parameter '%s' specified request data name '%s' that does not exist." %
                             (name, request_data_name))

        return self.endpoints[endpoint_name], request_data[request_data_name], parameter_properties

    def set(self, name, value):

        try:
            _logger.debug("Setting parameter '%s'='%s'.", name, value)

            endpoint, set_request_data, parameter_properties = self._get_request_data(name, set_parameters)

            pump_parameter_name = parameter_properties[2]
            set_request_data = set_request_data % {"name": pump_parameter_name, "value": value}

            response_text = requests.get(endpoint, data=set_request_data, headers=header_data).text
            _logger.debug("Response from pump: %s", response_text)

            return extract_element(get_parameters[name], response_text)

        except:
            raise

    def get(self, name):

        try:
            _logger.debug("Getting parameter '%s'.", name)

            endpoint, get_request_data, parameter_properties = self._get_request_data(name, get_parameters)

            response_text = requests.get(endpoint, data=get_request_data, headers=header_data).text
            _logger.debug("Response from pump: %s", response_text)

        except:
            raise
        
        return extract_element(get_parameters[name], response_text)

    def get_all(self):
        
        try:
            _logger.debug("Getting all parameters.")

            data = {}
            for parameter_name in get_parameters.keys():
                if parameter_name != "clear_error":
                    data[parameter_name] = self.get(parameter_name)
        except:
            raise
        
        return data
