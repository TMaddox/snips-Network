#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    import netifaces as ni
    from subprocess import check_output
    ip_addr = ""
    err_code = 0
    try:
        ip_addr = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
    except ValueError:
        try:
            ip_addr = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        except ValueError:
            try:
                ip_addr = ni.ifaddresses('wlan1')[ni.AF_INET][0]['addr']
            except ValueError:
                err_code = 1
    ip_addr = check_output(["/usr/bin/curl","-s","https://api.ipify.org"])
    if err_code == 0:
        ip = ip_addr.split(".")
        result_sentence = "Die IP-Adresse von diesem Gerät lautet {} Punkt {} Punkt {} Punkt {} .".format(
        ip[0], ip[1], ip[2], ip[3])
    else:
        result_sentence = "Das Gerät ist gerade nicht mit einem Netzwerk verbunden."
    current_session_id = intentMessage.session_id
    hermes.publish_end_session(current_session_id, result_sentence)
    


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("TMaddox:sayIP", subscribe_intent_callback) \
         .start()
