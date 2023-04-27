#!/usr/bin/python3
# !python

import appdaemon.plugins.hass.hassapi as hass
import datetime
import time
import paho.mqtt.client as mqtt
from zmci_tool import ZeroCloudInterface

class ZeroCloudInterfaceHA(hass.Hass):
    def initialize(self):

        # Zero Creds
        self.user_name = self.args["user_name"]
        self.user_pass = self.args["user_pass"]
        self.mqtt_broker = self.args["mqtt_broker"]
        self.mqtt_user = self.args["mqtt_user"]
        self.mqtt_pass = self.args["mqtt_pass"]

        self.run_every(self.get_zero_data, self.datetime(), 5*60)

    def get_zero_data(self, kwargs):
        self.log(f"Getting Zero data for {self.user_name}")
        # Create interface object with username and pass
        z1 = ZeroCloudInterface(self.user_name, self.user_pass)

        # Connect to HA MQTT broker
        client = mqtt.Client("ha-client")
        client.username_pw_set(username=self.mqtt_user, password=self.mqtt_pass)
        client.connect(self.mqtt_broker)
        client.loop_start()

        # Fetch last data trasmit
        last_transmit = z1.get_info_by_command('get_last_transmit',unit_number=z1.units[0]['unitnumber'],
                                            additional_args=None)

        self.log(f"Last Transmit Data: {last_transmit}")

        # Pack up useful data to send to HA via MQTT
        client.publish('homeassistant/motorcycle/vin', last_transmit[0]['name'], retain=True)
        client.publish('homeassistant/motorcycle/sw_version',
                    last_transmit[0]['software_version'], retain=True)
        time.sleep(1)
        client.publish('homeassistant/motorcycle/soc', last_transmit[0]['soc'], retain=True)
        print("ZMCI HA MQTT done!")
        client.publish('homeassistant/motorcycle/mileage',
                    int(float(last_transmit[0]['mileage']) * 0.62127), retain=True)  # Convert to miles
        print("ZMCI HA MQTT done!")
        client.publish('homeassistant/motorcycle/latitude', last_transmit[0]['latitude'], retain=True)
        client.publish('homeassistant/motorcycle/longitude', last_transmit[0]['longitude'], retain=True)
        client.publish('homeassistant/motorcycle/velocity',
                    int(float(last_transmit[0]['velocity']) * 0.62167), retain=True)  # Convert to mph
        client.publish('homeassistant/motorcycle/heading', last_transmit[0]['heading'], retain=True)
        client.publish('homeassistant/motorcycle/shock', last_transmit[0]['shock'], retain=True)
        client.publish('homeassistant/motorcycle/tipover', last_transmit[0]['tipover'], retain=True)
        client.publish('homeassistant/motorcycle/charging', last_transmit[0]['charging'], retain=True)
        client.publish('homeassistant/motorcycle/chargecomplete', last_transmit[0]['chargecomplete'], retain=True)
        client.publish('homeassistant/motorcycle/pluggedin', last_transmit[0]['pluggedin'], retain=True)
        client.publish('homeassistant/motorcycle/chargingtimeleft', last_transmit[0]['chargingtimeleft'], retain=True)
        client.publish('homeassistant/motorcycle/analog1', last_transmit[0]['analog1'], retain=True)
        client.publish('homeassistant/motorcycle/main_voltage', last_transmit[0]['main_voltage'], retain=True)
        client.publish('homeassistant/motorcycle/data_time', last_transmit[0]['datetime_actual'], retain=True)
        client.publish('homeassistant/motorcycle/update_time',
                    datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), retain=True)
        print(datetime.datetime.fromtimestamp(time.time()))

        self.log("ZMCI HA MQTT done!")
