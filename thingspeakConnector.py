from simplesub import MySubscriber
import requests
import threading
import json


class thingspeakConnector(object):

    def __init__(self, DeviceID, motionTopic,tempTopic,humidityTopic,soilhumTopic,alarmTopic, RESTServer, Resource):
        self.deviceID=DeviceID
        self.mtopic=motionTopic
        self.temptopic=tempTopic
        self.htopic=humidityTopic
        self.shtopic=soilhumTopic
        self.atopic=alarmTopic
        self.rest_server=RESTServer
        self.resource=Resource
        self.broker="mqtt.eclipse.org"
        self.updateFreq=15
        self.baseURL="https://api.thingspeak.com/update?api_key=C4WXT7JH1VL8CE6X&field"
        #field1=temp
        #field2=humi
        #field3=soilhumi
        #field4=Motionalarm
        #field5=Tempalarm
        #field6=waterflow
        #Timestamp managed by the Catalog

        #create mqtt subsribers
        self.tsub=MySubscriber(self.deviceID,self.temptopic,self.broker)
        self.hsub=MySubscriber(self.deviceID,self.htopic,self.broker)
        self.shsub=MySubscriber(self.deviceID,self.shtopic,self.broker)
        self.msub=MySubscriber(self.deviceID, self.mtopic,self.broker)
        self.asub=MySubscriber(self.deviceID, self.atopic,self.broker)

        #start the subscribers
        self.msub.start()
        self.tsub.start()
        self.hsub.start()
        self.shsub.start()
        self.asub.start()
        #start the cleaning
        #self.clean()
        

    def run(self):
        #Enter this function every self.updateFreq
        threading.Timer(self.updateFreq,self.run).start()
        #store data in data.json
        data={"Temperature":    str(self.tsub.lastmessage.payload),
              "Humidity":       str(self.hsub.lastmessage.payload),
              "Soil_humidity":  str(self.shsub.lastmessage.payload),
              "Motion":         str(self.msub.lastmessage.payload)
            }
        
        f=open("data.json","w")
        f.write(json.dumps(data))
        f.close()


        # get the last messages from subs
        #send to thingspeak
        requests.post(self.baseURL+"1="+str(self.tsub.lastmessage.payload))
        requests.post(self.baseURL+"2="+str(self.hsub.lastmessage.payload))
        requests.post(self.baseURL+"3="+str(self.shsub.lastmessage.payload))
        #workaround
        motion="0"
        if str(self.msub.lastmessage.payload)=="True":
            motion="1"

        requests.post(self.baseURL+"4="+motion)
        #requests.post(self.baseURL+"5="+self.asub.lastmessage.payload)




    def clean(self):
        # used for clean up devices with longer timestamp than 2 mins
        #right now 2 secs for troubleshooting
        threading.Timer(2,self.clean).start()
        #Check if device is registerd in catalog. If not, add it.
        getURL=self.rest_server+'/get_device_by_ID/'+str(self.deviceID)
        response=requests.get(getURL)
        if str(response.text)=="Not found":
            #add device
            requests.put(self.rest_server, json={"command": "new device","DeviceID": self.deviceID ,"Topic": self.mtopic,"REST": self.rest_server ,"Resource": self.resource})
            print("Added device"+self.deviceID)
        else:
            #Maybe add some verification here todo
            #refresh device
            requests.put(self.rest_server, json={"command": "refresh device","DeviceID": self.deviceID})
            print("Refreshed device :"+ self.deviceID)


        
if __name__ == "__main__":
    tsC=thingspeakConnector("thingspeakConnector","sensors/motion","sensors/temperature","sensors/humidity","sensors/soilhumidity","sensors/alarm","localhost:8080","Connects topics to thingspeak")
    tsC.run()

