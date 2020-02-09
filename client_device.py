#!/usr/bin/python3
import requests
import threading
import json
import time
class device(object):

    def __init__(self, DeviceID, Topic, RESTServer, Resource):
        self.deviceID=DeviceID
        self.topic=Topic
        self.rest_server=RESTServer
        self.resource=Resource
        #Timestamp managed by the Catalog

    def clean(self):
        # used for clean up devices with longer timestamp than 2 mins
        #right now 2 secs for troubleshooting
        threading.Timer(2,self.clean).start()
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
    #create device
    dev=device(3,"testtopic","http://localhost:8080","")
    #cleaning service
    dev.clean()
