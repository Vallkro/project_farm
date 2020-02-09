import Adafruit_DHT
from client_device import device
from simplepub import Simplepub
import time

#### Sensor setup from DHT11 example

## Init
# Set sensor type : Options are DHT11,DHT22 or AM2302
thsensor=Adafruit_DHT.DHT11
# Set GPIO sensor is connected to
thsensor_gpio=17
device_ID="raspberry"
mqtt_topic="sensors"
rest_server="http://localhost:8080"



## Add the new device
dev1=device(device_ID,mqtt_topic,rest_server,"Temp, humidity and motion")

#Create publisher
simpub=Simplepub(device_ID,'mqtt.eclipse.org',1883)
#client ID == device iD for now, just a number i guess (?)
simpub.start()
while True:
  

  # Use read_retry method. This will retry up to 15 times to
  # get a sensor reading (waiting 2 seconds between each retry).
  humidity, temperature = Adafruit_DHT.read_retry(thsensor, thsensor_gpio)
  # Reading the DHT11 is very sensitive to timings and occasionally
  # the Pi might fail to get a valid reading. So check if readings are valid.
  if humidity is not None and temperature is not None:
    #publish temp
    simpub.publish(mqtt_topic+"/temperature",temperature)
    #Publish humidity
    simpub.publish(mqtt_topic+"/humidity",humidity)
  else:
    print('Failed to get reading. Try again!')

  time.sleep(1)
  
