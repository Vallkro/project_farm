
# Code of the watering system module.
# The module receive information about the weather and different sensor of the raspberry pie board (3 topics)
# from a message broker using MQTT communication.
# The module has to manage the (simulated) water-flow that goes to the plants based on the information received from

# The module finally commmunicate with the home catalog of the system to declare itself (using REST communications)

# The topics that are used are :
# - motion
# - Temperature
# - weather (Gives the precipitation for the incoming days (8 different values going from 0 to 9
# - sensor/soilhumidity topic --> a kind of percentage

import json as js
import requests
import time
import threading
import paho.mqtt.client as PahoMQTT
from simplepub import Simplepub

class WateringSystem_Management:
    def __init__(self):
        self.watering_lvl_values = [0, 1, 2, 3]
        self.watering_lvl_nextday = [2, 2, 2, 2, 2, 2, 2, 2]
        self.watering_level_output=0 ##Couldnt init a variable w/o value in Linux, there is some other way to do it, todo

        self.important_precipitation = 7
        self.medium_precipitation = 5
        self.sparsely_precipitation = 3

        self.tmp_threshold = 25 #C
        self.low_soilhumidity = 20 # kind of percentage
        self.high_soilhumidity = 80 # kind of percentage

        #Init a publisher
        self.pub=Simplepub("Watering_system","mqtt.eclipse.org",1883)
        self.pub.start()


    def verify_precipitation_lvl(self, value_to_check):
        if (value_to_check > self.important_precipitation):
            return self.watering_lvl_values[0]
        elif (self.important_precipitation >= value_to_check and value_to_check >= self.medium_precipitation):
            return self.watering_lvl_values[1]
        elif (self.medium_precipitation > value_to_check and value_to_check >= self.sparsely_precipitation):
            return self.watering_lvl_values[2]
        else:
            return self.watering_lvl_values[3]


    def stop_water_flow(self):
        self.prev_value = self.watering_level_output
        self.watering_level_output = self.watering_lvl_values[0]


    def restart_water_flow(self):
        self.watering_level_output = self.prev_value


    def increase_water_flow(self):
        if (self.watering_level_output == self.watering_lvl_values[len(self.watering_lvl_values)-1]):
            print("The water flow cannot be increased, it is already at its maximal value")
        else:
            current_val = self.watering_lvl_values.index(self.watering_level_output)
            self.watering_level_output = self.watering_lvl_values[current_val+1]


    def decrease_water_flow(self):
        if (self.watering_level_output == self.watering_lvl_values[0]):
            print("The water flow cannot be decreased, it is already at its minimal value")
        else:
            current_val = self.watering_lvl_values.index(self.watering_level_output)
            self.watering_level_output = self.watering_lvl_values[current_val-1]


    def update_watering_levels(self, content):
        precipitation_level = [0, 0, 0, 0, 0, 0, 0, 0]
        precipitation_level[0] = content["three"]
        precipitation_level[1] = content["six"]
        precipitation_level[2] = content["nine"]
        precipitation_level[3] = content["twelve"]
        precipitation_level[4] = content["fifteen"]
        precipitation_level[5] = content["eighteen"]
        precipitation_level[6] = content["twenty_one"]
        precipitation_level[7] = content["twenty_four"]

        for i in range(len(precipitation_level)):
            self.watering_lvl_nextday[i] = self.verify_precipitation_lvl(precipitation_level[i])


    def run_watering_for_a_day(self):
        for i in range(len(self.watering_lvl_nextday)):
            self.watering_level_output = self.watering_lvl_nextday[i]
            time.sleep(10800) # 3 hours = 10 800 second

    def publish_waterflow(self):
        threading.Timer(5, self.publish_waterflow).start()
        self.pub.publish("polito/01QWRBH/SmartFarm/device1/outputs/waterflow",self.watering_level_output)






class WateringSystem_Subscriber:
    def __init__(self, clientID, deviceID, topics, broker, RESTServer):
        self.clientID = clientID
        self.deviceID = deviceID

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

        # define the topics
        self.motion_topic = topics[0]
        self.temperature_topic = topics[1]
        self.weather_topic = topics[2]
        self.soilhumidity_topic = topics[3]

        self.messageBroker = broker
        self.rest_server = RESTServer

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, 1883)
        self._paho_mqtt.loop_start()
        # subscribe for a topic
        self._paho_mqtt.subscribe(self.motion_topic, 2)
        self._paho_mqtt.subscribe(self.temperature_topic, 2)
        self._paho_mqtt.subscribe(self.weather_topic, 2)
        self._paho_mqtt.subscribe(self.soilhumidity_topic, 2)
        # create an object that manage the water flow
        self.watering_controler = WateringSystem_Management()
        self.watering_controler.publish_waterflow()

    def stop(self):
        self._paho_mqtt.unsubscribe(self.motion_topic)
        self._paho_mqtt.unsubscribe(self.temperature_topic)
        self._paho_mqtt.unsubscribe(self.weather_topic)
        self._paho_mqtt.unsubscribe(self.soilhumidity_topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        print("Topic:'" + msg.topic + "', QoS: '" + str(msg.qos) + "' Message: '" + str(msg.payload) + "'")

        if (msg.topic == self.motion_topic and str(msg.payload) == "True"):
            t1 = threading.Thread(target=self.watering_controler.stop_water_flow())
            t1.start()
            t1.join()

        if (msg.topic == self.motion_topic and str(msg.payload) == "False"):
            t1 = threading.Thread(target=self.watering_controler.restart_water_flow())
            t1.start()
            t1.join()

        if ((msg.topic == self.temperature_topic and int(msg.payload) > self.watering_controler.tmp_threshold) or
                (msg.topic == self.soilhumidity_topic and int(msg.payload) <= self.watering_controler.low_soilhumidity)):
            t1 = threading.Thread(target=self.watering_controler.increase_water_flow())
            t1.start()
            t1.join()

        if (msg.topic == self.soilhumidity_topic and int(msg.payload) >= self.watering_controler.high_soilhumidity):
            t1 = threading.Thread(target=self.watering_controler.decrease_water_flow())
            t1.start()
            t1.join()

        if (msg.topic == self.weather_topic):
            self.watering_controler.update_watering_levels(msg.payload)
            t0 = threading.Thread(target=self.watering_controler.run_watering_for_a_day())
            t0.start()


    def clean(self):
        # used for clean up devices with longer timestamp than 2 mins
        # right now 2 secs for troubleshooting
        threading.Timer(10, self.clean).start()

        # Check if device is registerd in catalog. If not, add it.
        getURL = self.rest_server + '/get_device_by_ID/' + str(self.deviceID)
        response = requests.get(getURL)
        #print(response.text)
        if str(response.text) == "Not found":
            # add device
            requests.put(self.rest_server, json={"command": "new device", "DeviceID": self.deviceID, "Topics": [self.motion_topic, self.temperature_topic, self.weather_topic, self.soilhumidity_topic]})
            print("ADDED")
        else:
            # Maybe add some verification here todo
            # refresh device
            requests.put(self.rest_server, json={"command": "refresh device", "DeviceID": self.deviceID})
            print("Refreshed "+self.clientID)



if __name__ == '__main__':
    clientID = "wateringSystem"
    deviceID = 1
    topics = [ "polito/01QWRBH/SmartFarm/device1/sensors/motion", "polito/01QWRBH/SmartFarm/device1/sensors/temperature", "polito/01QWRBH/SmartFarm/weatherForecast", "polito/01QWRBH/SmartFarm/device1/sensors/soilhumidity"]
    broker = "mqtt.eclipse.org"
    RESTServer = "http://localhost:8080"

    waterin = WateringSystem_Subscriber(clientID, deviceID, topics, broker, RESTServer)
    waterin.start()
    waterin.clean()

    


    while True:
        pass
        print("Currently working")
        time.sleep(3)

    waterin.stop()