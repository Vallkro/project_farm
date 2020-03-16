# This file corresponds to the alarm controller component.
# This component has to raise an alarm if the motien sensor of the Raspbberry Pi is indicating that the plant is moving or if
# a particular temperature threshold is crossed (when it is too warm). Those alarms are send to the data collector component
# so that it can manage then by warn the user of the system that a weird behaviour happened.

# The alarm controller component subscribed to the temperature and motion topics to the message broker.
# The alarm are send to the data collector thanks to the alarm topic (MQTT)

from simplepub import Simplepub

import json as js
import datetime
import requests
import threading
import paho.mqtt.client as PahoMQTT


class Alarm_communication:
    def __init__(self, clientID, deviceID, topics, broker, RESTServer, temperature_threshold = 35):
        self.clientID = clientID
        self.deviceID = deviceID
        self.temp_thresh = temperature_threshold

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        self.temperature_topic = topics[0]
        self.motion_topic = topics[1]
        self.alarm_topic = topics[2]
        self.messageBroker = broker
        self.rest_server = RESTServer
        self.pub=Simplepub(self.deviceID,broker,1883)
        self.pub.start()

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.temperature_topic, 2)
        self._paho_mqtt.subscribe(self.motion_topic, 2)

    def stop(self):
        self.pub.stop()
        self._paho_mqtt.unsubscribe(self.temperature_topic)
        self._paho_mqtt.unsubscribe(self.motion_topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    # This component will only transmit at what time the condition to raise an alarm are met
    # It will not do anything to modify the behavior of the system when those alarms occur
    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        msg.payload = msg.payload.decode("utf-8")
        print("Topic:'" + msg.topic + "', QoS: '" + str(msg.qos) + "' Message: '" + str(msg.payload) + "'")
        time_now=str(datetime.datetime.now()) ## workaround
        # Verify if the message is related to the motion topic and if it's indicate a movement
        if (msg.topic == self.motion_topic and str(msg.payload) == "True"):
            print("ALARM!!!!")
            # Publish a message under the alarm topic indicating the nature of the alarm and the time at which it happens
            alarm_message = {"nature":"motion",
                        "time": time_now}
            self.pub.publish(self.alarm_topic,str(alarm_message))
            
            #self.myPublish(self.alarm_topic, js.dumps({"nature": "motion", "time": datetime.datetime.now()}))
            print("Message published")

        
        # Verify of the message is related to the temperature topic and if the indicated temperature is above the threshold
        if (msg.topic == self.temperature_topic and float(msg.payload) >= float(self.temp_thresh)):
            print("TEMPERATURE_ALARM!!!")
            
            # Publish a message under the alarm topic indicating the nature of the alarm and the time at which it happens
            
            tempalarm_message={"nature": "Temperature","Value": str(msg.payload), "time": time_now}
            #self.myPublish(self.alarm_topic, js.dumps({"nature": "Temperature", "time": datetime.datetime.now()}))
            self.pub.publish(self.alarm_topic,str(tempalarm_message))

            print("Message published")

    def myPublish(self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, msg, 2)
        print("Publishing : "+ str(msg))

    def clean(self):
        # used for clean up devices with longer timestamp than 2 mins
        # right now 2 secs for troubleshooting
        threading.Timer(2, self.clean).start()

        # Check if device is registerd in catalog. If not, add it.
        getURL = self.rest_server + '/get_device_by_ID/' + str(self.deviceID)
        response = requests.get(getURL)
        #print(response.text)
        if str(response.text) == "Not found":
            # add device
            requests.put(self.rest_server, json={"command": "new device", "DeviceID": self.deviceID, "Topics": [self.temperature_topic, self.motion_topic, self.alarm_topic]})
            #print("ADDED")
        else:
            # Maybe add some verification here todo
            # refresh device
            requests.put(self.rest_server, json={"command": "refresh device", "DeviceID": self.deviceID})
            #print("REFRESHED")

if __name__ == '__main__':

    clientID = "AlarmController"
    deviceID = "AlarmController"
    topics = ["polito/01QWRBH/SmartFarm/device1/sensors/temperature", "polito/01QWRBH/SmartFarm/device1/sensors/motion", "polito/01QWRBH/SmartFarm/device1/sensors/alarm"]
    RESTServer = "http://localhost:8080"
    broker = "mqtt.eclipse.org"

    print("Indicate a threshold value for the temperature (the default value is 35°C)")
    temperature = input()

    alarm = Alarm_communication(clientID, deviceID, topics, broker, RESTServer, temperature)
    alarm.start()
    alarm.clean()