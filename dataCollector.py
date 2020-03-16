import paho.mqtt.client as PahoMQTT
from telegram.ext import Updater, CommandHandler
import time
import threading
import requests
import json

#It must subscribe to all the topics in the program 
class MySubscriber(object):

	def __init__(self, clientID,topic,broker,RESTServer,Resource):
		self.clientID = clientID
		# create an instance of paho.mqtt.client
		self._paho_mqtt = PahoMQTT.Client(clientID, False) 

		# register the callback
		self._paho_mqtt.on_connect = self.myOnConnect
		self._paho_mqtt.on_message = self.myOnMessageReceived

		self.topic = topic
		self.messageBroker =broker 

		self.alarm_value = "<no value>"
		self.temp_value = "<no value>"
		self.hume_value = "<no value>"
		self.soil_hume_value = "<no value>"
		self.water_used = "<no value>"

		self.rest_server=RESTServer
		self.resource=Resource
		self.deviceID = clientID

		self.chat_id_list = []

	def start (self):
		#manage connection to broker
		self._paho_mqtt.connect(self.messageBroker, 1883)
		self._paho_mqtt.loop_start()
		# subscribe for a topic
		self._paho_mqtt.subscribe(self.topic, 0)
		

	def stop (self):
		self._paho_mqtt.unsubscribe(self.topic)
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print ("Connected to %s with result code: %d" % (self.messageBroker, rc))

	
	#These 4 functions are used for the telegram bot
	def temperature(self,bot,update):
		chat_id = update.message.chat_id
		bot.sendMessage(chat_id,"The temperature is: "+self.temp_value+"ºC")

	def humidity(self,bot,update):
		chat_id = update.message.chat_id
		bot.sendMessage(chat_id,"The humidity is: "+self.hume_value+"%")

	def soil_humidity(self,bot,update):
		chat_id = update.message.chat_id
		bot.sendMessage(chat_id,"The soil humidity is: " + self.soil_hume_value + "")

	def water_used(self,bot,update):
		chat_id = update.message.chat_id
		bot.sendMessage(chat_id,self.water_used)

	def subscribe_to_alarm(self,bot,update):
		chat_id = str(update.message.chat_id)
		#update the chat_ids
		if chat_id in self.chat_id_list:
			bot.sendMessage(chat_id,"Already subscribed!")
		else:
			self.chat_id_list.append(chat_id)
			print("New user with : "+chat_id+" subscribed to alarm notifications")
			print(self.chat_id_list)
			bot.sendMessage(chat_id,"Subscribed succesfully!")
		

	def unsubscribe_to_alarm(self,bot,update):
		chat_id = str(update.message.chat_id)
		
		if chat_id in self.chat_id_list:
			self.chat_id_list.remove(chat_id)
			print("User with chat_id: " + chat_id + " unsubscribed to alarm notifications.")
			print(self.chat_id_list)
			bot.sendMessage(chat_id,"Unsubscribed succesfully!")
		else:
			bot.sendMessage(chat_id,"Not subscribed yet")

	def myOnMessageReceived (self, paho_mqtt , userdata, msg):
		# A new message is received
		# Everytime it receives a new message it sends the information to telegram
		if msg.topic == "polito/01QWRBH/SmartFarm/device1/sensors/alarm":
			self.alarm_value = "There is an alarm situation"
			msg.payload = msg.payload.decode("utf-8")
			print ('Topic:' + msg.topic+', QoS: '+str(msg.qos)+' Message: '+ str(msg.payload))

			for i in self.chat_id_list:
				dp.bot.sendMessage(i,"ALARM!")
				dp.bot.sendMessage(i,str(msg.payload)) #It's sending to telegram the json itself, but we couldn't parse it well 
 

		elif msg.topic == "polito/01QWRBH/SmartFarm/device1/sensors/temperature":
			msg.payload = msg.payload.decode("utf-8")
			#print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")
			self.temp_value = str(msg.payload)

		elif msg.topic == "polito/01QWRBH/SmartFarm/device1/sensors/soilhumidity": 
			msg.payload = msg.payload.decode("utf-8")
			#print ("Topic:'" + msg.topic+"', QoS: '"+str(msg.qos)+"' Message: '"+str(msg.payload) + "'")
			self.soil_hume_value = str(msg.payload)

		elif msg.topic == "polito/01QWRBH/SmartFarm/device1/sensors/humidity":
			msg.payload = msg.payload.decode("utf-8")
			#print ('Topic:' + msg.topic+', QoS: '+str(msg.qos)+' Message: '+str(msg.payload))
			self.hume_value = str(msg.payload)


	def clean(self):
	# used for clean up devices with longer timestamp than 2 mins
		#right now 2 secs for troubleshooting
		threading.Timer(2,self.clean).start()
			# Do the cleaning later
	

		#Check if device is registerd in catalog. If not, add it.
		getURL=self.rest_server+'/get_device_by_ID/'+str(self.deviceID)
		response=requests.get(getURL)
		#print(response.text)
		if str(response.text)=="Not found":
			#add device
			requests.put(self.rest_server, json={"command": "new device","DeviceID": self.deviceID ,"Topic": self.topic,"REST": self.rest_server ,"Resource": self.resource})
			#print("ADDED")
		else:
			#Maybe add some verification here todo
			#refresh device
			requests.put(self.rest_server, json={"command": "refresh device","DeviceID": self.deviceID})
			#print("REFRESHED")




if __name__ == "__main__":

	test = MySubscriber("dataCollector","polito/01QWRBH/SmartFarm/+",'mqtt.eclipse.org','http://192.168.1.10:8080','dataCollector') 
	#It uses the wild card # to listen to all the topics
	updater = Updater('1124002256:AAEtMOjpwbQNyFPa-O7Nv0dQiy_kFy_IF1A')
	dp = updater.dispatcher

	test.start()
	test.clean()
	#Telegram bot configuration

	dp.add_handler(CommandHandler('temperature',test.temperature))
	dp.add_handler(CommandHandler('humidity',test.humidity))
	dp.add_handler(CommandHandler('soil_humidity',test.soil_humidity))
	#dp.add_handler(CommandHandler('water_used',test.water_used))
	dp.add_handler(CommandHandler('subscribe_to_alarm',test.subscribe_to_alarm))
	dp.add_handler(CommandHandler('unsubscribe_to_alarm',test.unsubscribe_to_alarm))
	updater.start_polling()
	updater.idle()





