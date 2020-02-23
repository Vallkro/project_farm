import Adafruit_DHT
import RPi.GPIO as GPIO
import time
import threading
import math


# From other classes
from client_device import device
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
        # Add the new device
        self.dev1 = device(self.device_ID, self.mqtt_topic, self.rest_server,
                      "Temp, humidity and motion")
        # Create a publisher
        self.simpub = Simplepub(self.device_ID, self.broker, 1883)
        # client ID == device iD for now, just a number i guess (?)
	
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

    deviceID = "raspberry"
    mqtt_topic = "sensors"
    restServer = "http://localhost:8080"
    broker='mqtt.eclipse.org'
    dc=Device_Connector(deviceID,broker,mqtt_topic,restServer,2)
    dc.start()
    dc.start_publish()

    time.sleep(20)
    dc.stop()

    
    
