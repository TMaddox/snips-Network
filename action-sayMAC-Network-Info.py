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
	
	mac = ""
	err_code = 0
	iface = "null"

	try:
		ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
		mac = ni.ifaddresses('wlan0')[ni.AF_LINK][0]['addr']
		iface = wlan0
	except ValueError:
		try:
			ip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
			mac = ni.ifaddresses('eth0')[ni.AF_LINK][0]['addr']
			iface = eth0
		except ValueError:
			try:
				ip = ni.ifaddresses('wlan1')[ni.AF_INET][0]['addr']
				mac = ni.ifaddresses('wlan1')[ni.AF_LINK][0]['addr']
				iface = wlan1
			except ValueError:
				err_code = 1
	if err_code == 0:
		mac_out = mac.upper().split(":")
		result_sentence = "Die mac Adresse von {} lautet {} . {} . {} . {} . {} . {} .".format(iface, mac_out[0], mac_out[1], mac_out[2], mac_out[3], mac_out[4], mac_out[5])
	else:
		result_sentence = "Das Gerät ist gerade nicht mit einem Netzwerk verbunden."
	current_session_id = intentMessage.session_id
	hermes.publish_end_session(current_session_id, result_sentence)
    


if __name__ == "__main__":
    with Hermes("localhost:1883") as h:
        h.subscribe_intent("TMaddox:sayMAC", subscribe_intent_callback) \
         .start()
