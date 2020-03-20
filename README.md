# Smart Farm project

## Program descriptions



**RESTcatalog.py**

- Home server, uses GET, PUT,POST to send and process data
- Deploys freeboard
- Publishes ip using mqtt
- Stores data in data.json,devices.json,users.json.

**device\_connector.py**

- Must be run on raspberry pi
- Uses Adafruit\_DHT, RPi.GPIO libraries
- Reads sensor data, publishes to respective mqtt topics.

**emulatedsoilpub.py**

- Mqtt publisher and subscriber.
- Depends on temp, humidity and waterflow.

**simplepub.py**

- Bare bones publisher, used in RESTcatalog, emulatedsoilpub, device\_connector, watering system

**simplesub.py**

- Bare bones subscriber, used in device\_connector, thingspeakConnector,emulatedsoilpub

**thingspeakConnector.py**

- Displays all the values over time
- Mqtt subscriber to all of the topics, POST data to thingspeak
- [https://thingspeak.com/channels/1011118](https://thingspeak.com/channels/1011118)
- saves data to data.json (currently a workaround, but works)

**alarm\_controller.py**

- **●●** Mqtt publisher and subscriber
- **●●** Subscribes to &#39;Motion&#39; and &#39;Temperature&#39; topics data, publishes to &#39;alarm&#39; topic if a movement is detected or temperature too high

**watering\_system.py**

- Mqtt subscriber
- Subscribes to mqtt topics and controls the waterflow, to keep the soilhumidity at a good level.
- Subscribes to &#39;Motion&#39; topic and stop the waterflow if a movement is detected.

**dataCollector.py       **

- subscribes to mqtt topics and connects the telegram bot

**wheatherController.py**

- connetcs to an external wheater forecast API
- publishes to wheathertopic

**freeboard**

- Displays Current temperature, humidity, waterflow and soilhumidity.
- GET requests to home server to get data
- POST requests to save dashboard

## Topic descriptions

**Wheater topic**

polito/01QWRBH/SmartFarm/weatherForecast

mqtt publisher of the wheater forecast

ex json:

{&quot;three&quot;: 0, &quot;six&quot;: 0, &quot;nine&quot;: 1, &quot;twelve&quot;: 1, &quot;fifteen&quot;: 1, &quot;eighteen&quot;: 1, &quot;twenty\_one&quot;: 1, &quot;twenty\_four&quot;: 1}

**Alarm topic:**

polito/01QWRBH/SmartFarm/device1/sensors/alarm

Json only if alarm is raised. Ex:

{&#39;nature&#39;: &#39;Temperature&#39;, &#39;Value&#39;: &#39;19.0&#39;, &#39;time&#39;: &#39;2020-03-16 17:18:51.008323&#39;}

**Humidity topic**

polito/01QWRBH/SmartFarm/device1/sensors/humidity

Float every 5.

**Soil humidity topic:**

polito/01QWRBH/SmartFarm/device1/sensors/soilhumidity

Float every 5, emulated value.

**Temp topic:**

polito/01QWRBH/SmartFarm/device1/sensors/temperature

Float every 5 seconds

**Motion topic:**

polito/01QWRBH/SmartFarm/device1/sensors/motion

Bool every 5 seconds, True if motion detected

**Ip topic:**

polito/01QWRBH/SmartFarm/home/ip

String every 5. Ip of home server

Used for initializing a new connection.

**Waterflow topic:**

polito/01QWRBH/SmartFarm/device1/outputs/waterflow

Float every 5.





## Included libraries

- cherrypy
- json
- paho.mqtt.client
- time
- threading
- from os.path import abspath
- socket
- requests
- math
- from telegram.ext import Updater, CommandHandler
- urllib
- datetime
- Adafruit_DHT
- RPi.GPIO
