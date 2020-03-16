import urllib
import requests
import json
import time
import paho.mqtt.client as PahoMQTT
import datetime 
import threading 
import cherrypy

class MyPublisher(object):
	def __init__(self, clientID,  DeviceID, Topic, RESTServer, Resource):
		self.clientID = clientID
		self.deviceID=DeviceID
		self.topic=Topic
		self.rest_server=RESTServer
		self.resource=Resource

		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(self.clientID, False) 
		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect

		#self.messageBroker = 'iot.eclipse.org'
		self.messageBroker = 'mqtt.eclipse.org'

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()

	def stop (self):
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, message):
		# publish a message with a certain topic
		self._paho_mqtt.publish(self.topic, message, 2)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

	def clean(self):
	# used for clean up devices with longer timestamp than 2 mins
		#right now 2 secs for troubleshooting
		threading 	.Timer(2,self.clean).start()
			# Do the cleaning later
	

		#Check if device is registerd in catalog. If not, add it.
		getURL=self.rest_server+'/get_device_by_ID/'+str(self.deviceID)
		response=requests.get(getURL)
		print(response.text)
		if str(response.text)=="Not found":
			#add device
			requests.put(self.rest_server, json={"command": "new device","DeviceID": self.deviceID ,"Topic": self.topic,"REST": self.rest_server ,"Resource": self.resource})
			print("ADDED")
		else:
			#Maybe add some verification here todo
			#refresh device
			requests.put(self.rest_server, json={"command": "refresh device","DeviceID": self.deviceID})
			print("REFRESHED")

if __name__ == '__main__':

	weather = MyPublisher("WeatherPublisher","DeviceID","polito/01QWRBH/SmartFarm/weatherForecast","http://localhost:8080","weather")
	weather.start()

	periodic = False
	weather.clean()
	
	while(True):

		if periodic == False:
			#It means that the code is being ran for the first time 

			print("---- WELCOME TO THE WEATHER FORECAST APPLICATION ----\n\n")

			url = "http://www.7timer.info/bin/civil.php?lon=-0.118092&lat=51.509865&ac=0&unit=metric&output=json&tzshift=0"
			data_json2 = requests.get(url).json()

			daily_rain = {
				'three':data_json2['dataseries'][0]['prec_amount'],
				'six':data_json2['dataseries'][1]['prec_amount'],
				'nine':data_json2['dataseries'][2]['prec_amount'],
				'twelve':data_json2['dataseries'][3]['prec_amount'],
				'fifteen':data_json2['dataseries'][4]['prec_amount'],
				'eighteen':data_json2['dataseries'][5]['prec_amount'],
				'twenty_one':data_json2['dataseries'][6]['prec_amount'],
				'twenty_four':data_json2['dataseries'][7]['prec_amount']
			}

			daily_rain_string = json.dumps(daily_rain)

			print(daily_rain_string)

			#It should get the weather information right at the moment when it starts running,
			#and then every at midnight. (00:01). By now I'm gonna leave it like this, 
			#so I can test it well 
			weather.myPublish(daily_rain_string)

			#The program should sleep until midnight, when it's time to send the forecast again
			print("Information sent")
			time.sleep(3)

			# currentDT = datetime.datetime.now()
			# hour = currentDT.hour
			# minute = currentDT.minute
			# hoursToMidNight = 24 - int(hour) +1
			# minutesToNextHour = 60 - int(minute)
			# secondsToMidnight = hoursToMidNight*60*60 + minutesToNextHour*60

			# time.sleep(secondsToMidnight)

			periodic = True

		else:

			#It means that the code is being ran after the first time 

			print("---- WELCOME TO THE WEATHER FORECAST APPLICATION ----\n\n")

			url = "http://www.7timer.info/bin/civil.php?lon=-0.118092&lat=51.509865&ac=0&unit=metric&output=json&tzshift=0"
			data_json2 = requests.get(url).json()

			daily_rain = {
				'three':data_json2['dataseries'][0]['prec_amount'],
				'six':data_json2['dataseries'][1]['prec_amount'],
				'nine':data_json2['dataseries'][2]['prec_amount'],
				'twelve':data_json2['dataseries'][3]['prec_amount'],
				'fifteen':data_json2['dataseries'][4]['prec_amount'],
				'eighteen':data_json2['dataseries'][5]['prec_amount'],
				'twenty_one':data_json2['dataseries'][6]['prec_amount'],
				'twenty_four':data_json2['dataseries'][7]['prec_amount']
			}

			daily_rain_string = json.dumps(daily_rain)

			print(daily_rain_string)

			#It should get the weather information right at the moment when it starts running,
			#and then every at midnight. (00:01). By now I'm gonna leave it like this, 
			#so I can test it well 
			weather.myPublish(daily_rain_string)

			print("Information sent")
			time.sleep(3)

			#time.sleep(24*60*60)

		

	weather.stop()