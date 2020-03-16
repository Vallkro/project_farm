import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import threading
import math
import requests


# From other classes
from simplepub import Simplepub


class Device_Connector(object):
    def __init__(self, DeviceID,Broker, Topic, RestServer,Freq):
        self.run=False
        self.freq=Freq
        # Setup rest and mqtt connections
        self.device_ID = DeviceID
        self.mqtt_topic = Topic
        self.rest_server = RestServer
        self.broker=Broker
        self.resource="Temp, humidity and motion sensors"
        # Sensor setup from DHT11 example
        # Init
        # Set sensor type : Options are DHT11,DHT22 or AM2302
        self.thsensor = Adafruit_DHT.DHT11
        # Set GPIO sensor is connected to
        self.thsensor_gpio = 17
        self.msensor_gpio = 22
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.msensor_gpio, GPIO.IN)
        # Motion sensor needed some time to initialize
        print("Init...")
        time.sleep(3)

        # Create a publisher
        self.simpub = Simplepub(self.device_ID, self.broker, 1883)
        # client ID == device iD for now, just a number i guess (?)

    def clean(self):
        # used for clean up devices with longer timestamp than 2 mins
        #right now 2 secs for troubleshooting
        threading.Timer(2,self.clean).start()
        # Do the cleaning later
        

        #Check if device is registerd in catalog. If not, add it.
        getURL=self.rest_server+'/get_device_by_ID/'+str(self.device_ID)
        response=requests.get(getURL)
        print(response.text)
        if str(response.text)=="Not found":
            #add device
            requests.put(self.rest_server, json={"command": "new device","device_ID": self.device_ID ,"Topic": self.mqtt_topic,"REST": self.rest_server ,"Resource": self.resource})
            print("ADDED")
        else:
            #Maybe add some verification here todo
            #refresh device
            requests.put(self.rest_server, json={"command": "refresh device","device_ID": self.device_ID})
            print("REFRESHED")

	
    def start_publish(self):
        if self.run==True:
            # When true, run this function every freq seconds
            threading.Timer(self.freq,self.start_publish).start()

            ##### Read data
            # Use read_retry method. This will retry up to 15 times to
            # get a sensor reading (waiting 2 seconds between each retry).
            humidity, temperature = Adafruit_DHT.read_retry(self.thsensor, self.thsensor_gpio)
            # Reading the DHT11 is very sensitive to timings and occasionally
            # the Pi might fail to get a valid reading. So check if readings are valid.

            # Read motion
            motion = GPIO.input(self.msensor_gpio)

            ## Publish it
            self.simpub.publish(self.mqtt_topic+"/motion", bool(motion))
            if humidity is not None and temperature is not None:
                # publish temp
                self.simpub.publish(self.mqtt_topic+"/temperature", temperature)
                # Publish humidity
                self.simpub.publish(self.mqtt_topic+"/humidity", humidity)
            else:
                print('Failed to get reading of temp or humidity')

    
    def stop(self):
        self.simpub.stop()
        self.run=False
        GPIO.cleanup()

    def start(self):
        self.run=True
        self.simpub.start()

		

if __name__ == "__main__":

    deviceID = "device1"
    mqtt_topic = "polito/01QWRBH/SmartFarm/device1/sensors"
    restServer = "http://192.168.1.10:8080"
    broker='mqtt.eclipse.org'
    dc=Device_Connector(deviceID,broker,mqtt_topic,restServer,5)
    dc.start()
    dc.start_publish()
    dc.clean()
    while True:
        time.sleep(20) ## only for testing purp, delete when rdy, todo
    dc.stop()

    
    
