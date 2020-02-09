import paho.mqtt.client as PahoMQTT
import time

class Simplepub:

    def __init__(self,clientID,broker,port):

        self.clientID=clientID
        #create instance of pahomqqtclient
        self._paho_mqtt=PahoMQTT.Client(self.clientID,False)
        #register the callback
        self._paho_mqtt.on_connect=self.myOnconnect
        self.messagebroker = broker
        self.port=port

    def start (self):
        #manage connenction to broker
        self._paho_mqtt.connect(self.messagebroker,self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def publish(self,topic,message):
        #publish message to topic
        self._paho_mqtt.publish(topic,message,2) 
        print("Publishing :"+str(message)+" Topic: "+topic)

    def myOnconnect(self, paho_mqtt,userdata,flags,rc):

        print("Connected to %s with result code: %d"% (self.messagebroker,rc))

if __name__=="__main__":

    sp=Simplepub(1337,'mqtt.eclipse.org',1883)
    sp.start()
    
    while True:
        sp.publish("bajstopic","korvmebro")
        time.sleep(1)
