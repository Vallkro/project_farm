#!/usr/bin/python3
import cherrypy
import json
import paho.mqtt.client as PahoMQTT
import time
import threading
from os.path import abspath
import os
from simplepub import Simplepub
import socket



class Catalog(object):

    exposed = True

    def __init__(self):
        self.messageBroker = 'mqtt.eclipse.org'
        self.port = 1883
        self.devices = []
        # Load json files
        f = open("users.json", "r")
        self.users = json.load(f)
        f.close()

        f = open("devices.json", "r")
        self.devices = json.load(f)
        f.close()

        f=open("data.json","r")
        self.data=json.load(f)
        f.close()






    def GET(self, *uri, **params):
        #lists to put stuff in 
        ops = []
        operand = ""

        # get uri into a list
        i = 1
        print(f"URI     : {uri}")

        if len(uri) > 1:
            for key in range(1, len(uri)):

                ops.append(uri[key])
                if i == len(uri)-1:
                    operand += uri[key]
                else:
                    operand += uri[key]+" "

                i += 1
        elif len(uri)==0:
            return open("freeboard/index.html","r").read()

        
        user_input = uri[0]  # search by uri0
        ## Possible to delete below by storing global vars in json instead, possible a global json, todo
        if user_input == "static":
            return open("freeboard/index.html","r").read()
        if user_input == "messagebroker":
            return json.dumps(self.messageBroker)

        if user_input == "port":
            return json.dumps(self.port)

        if user_input == "get_devices":
            return json.dumps(self.devices)

        if user_input == "get_device_by_ID":
            found = False
            for dev in self.devices["device_list"]:
                if str(dev["DeviceID"]) == str(ops[0]):
                    found = True
                    return json.dumps(dev)

            if found == False:
                return"Not found"

        if user_input == "get_users":
            return json.dumps(self.users)

        if user_input == "get_user_by_ID":
            found = False
            for usr in self.users["user_list"]:
                if str(usr["userID"]) == str(ops[0]):
                    found = True
                    return json.dumps(usr)

            if found == False:
                return"Not found"

        if user_input =="get_data":
            return open("data.json")

        else:
            raise NotImplementedError(" Function does not exist yet. ")

    def PUT(self, **params):
        body = cherrypy.request.body.read()
        json_body = json.loads(body.decode('utf-8'))
        ops = list(json_body.values())
        command = list(json_body.values())[0]
        response = " "

        print(f" JSON BODY : {list(json_body.values())} \n OPS : {ops} \n COMMAND : {command}")

        #There must be a fancier way of doing this
        if command == "new device":
            newDevice = {}
            newDevice["DeviceID"] = ops[1]
            newDevice["Topic"] = ops[2]
            newDevice["Resource"] = ops[3]
            newDevice["Timestamp"] = time.time()

            # write to file
            # maybe add a try e case here
            self.devices["device_list"].append(newDevice)
            f = open("devices.json", "w")
            f.write(json.dumps(self.devices))
            f.close

            response = "Added a new device with ID:"+str(ops[1])
            print(response)
            return json.dumps(response)

        if command== "refresh device":
            found = False
            for dev in self.devices["device_list"]:
                if str(dev["DeviceID"]) == str(ops[1]):
                    found = True

                    dev["Timestamp"]=time.time()
                    f = open("devices.json", "w")
                    f.write(json.dumps(self.devices))
                    f.close

                    response="refreshed device with ID: "+str(ops[1])
                    print(f"refreshed device with ID: {ops[1]}")
                    return json.dumps(response)

            if found == False:
                return"Not found"


        if command == "new user":
            newUser = {}
            newUser["userID"] = ops[1]
            newUser["name"] = ops[2]
            newUser["surname"] = ops[3]
            newUser["email"] = ops[4]

            # write to file
            # maybe add a try e case here
            self.users["user_list"].append(newUser)
            f = open("users.json", "w")
            f.write(json.dumps(self.users))
            f.close

            response = "Added a new user with ID:"+str(ops[1])
        print(response)
        return json.dumps(response)

    def POST(self,*uri, **params):
        
        #The freeboard function "Save freeboard" sends a POST request with
        if uri[0]=="saveDashboard":
            #and the save configs "json_string" as parameters
            #Overwrite the old dashboard.json with the new 
            f=open("freeboard/dashboard/dashboard.json","w")

            f.write(params["json_string"])
            f.close

def publishIp():
    #Should be in a separe file, but wanted to keep ippublisher running along the Server, to increase flexibility
    threading.Timer(120,publishIp).start()

        #Get IP and publish it using mqtt
    hostname = socket.gethostname() 
    IPAddr = socket.gethostbyname(hostname) 
    ipPub=Simplepub("Home","mqtt.eclipse.org",1883)
    ipPub.start()
    ipPub.publish("SmartFarm/home/ip",IPAddr)
            
# Not part of catalog class
if __name__ == '__main__':
    publishIp() #publish the ip adress of the home server every 2 mins

    FB_PATH = os.getcwd()

    #Server stuff
    conf={
        # The freeboard main page is exposed at the "/" path
        "/":{
            # Method dispatcher of the cherrypy library. When an HTTP request is received
            # the dispatcher merges the request type (GET, POST, etc.) with the relative
            # method of the WebService() class.
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            # The directory defined in the FB_PATH variable is taken as static and the
            # URI path "/" is associated to it
            'tools.staticdir.root': FB_PATH
        },
        # The following lines are the static directories definitions associated to the relative
        # paths
        "/css":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"freeboard/css"
        },
        "/js":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"freeboard/js"
        },
        "/img":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"freeboard/img"
        },
        "/plugins":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"freeboard/plugins"
        },
        "/dashboard":{
            'tools.staticdir.on':True,
            'tools.staticdir.dir':"freeboard/dashboard"
        }
    }

    # The WebService() class is exposed at the "/" URI path by using the configuration defined
    # in the conf variable
    cherrypy.tree.mount(Catalog(), "/", conf)
    # WebService() IP and port assignment
    cherrypy.server.socket_host = "0.0.0.0"
    cherrypy.server.socket_port = 8080
    # WebService() starting
    cherrypy.engine.start()
    cherrypy.engine.block()