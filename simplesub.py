import paho.mqtt.client as PahoMQTT
import time


class MySubscriber:
		def __init__(self, clientID, topic, broker):
			self.clientID = clientID
			# create an instance of paho.mqtt.client
			self._paho_mqtt = PahoMQTT.Client(clientID, False)
			# register the callback
			self._paho_mqtt.on_connect = self.myOnConnect
			self._paho_mqtt.on_message = self.myOnMessageReceived
			self.topic = topic
			self.messageBroker = broker
			self.lastmessage = None

		def start(self):
			# manage connection to broker
			self._paho_mqtt.connect(self.messageBroker, 1883)
			self._paho_mqtt.loop_start()
			# subscribe for a topic
			self._paho_mqtt.subscribe(self.topic, 2)

		def stop(self):
			self._paho_mqtt.unsubscribe(self.topic)
			self._paho_mqtt.loop_stop()
			self._paho_mqtt.disconnect()

		def myOnConnect(self, paho_mqtt, userdata, flags, rc):
			print("Connected to %s with result code: %d" % (self.messageBroker, rc))

		def myOnMessageReceived(self, paho_mqtt, userdata, msg):
			# A new message is received
			#check to see if the message is from the actual topic
			if str(msg.topic)==str(self.topic):
				msg.payload = msg.payload.decode("utf-8")
				self.lastmessage = msg

				print("Topic:" + msg.topic+", QoS: " +str(msg.qos)+" Message: "+msg.payload)


if __name__ == "__main__":

	while True:
		time.sleep(10)
