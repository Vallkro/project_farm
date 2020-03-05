#!/usr/bin/python3
import cherrypy
import json
import paho.mqtt.client as PahoMQTT
import time
import threading

class Catalog(object):

    exposed = True

    def __init__(self):
        self.messageBroker = 'mqtt.ecliplse.org'
        self.port = 1883
        self.devices = []
        # Load json files
        f = open("users.json", "r")
        self.users = json.load(f)
        f.close()

        f = open("devices.json", "r")
        self.devices = json.load(f)
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
            return "Project farm homepage use : \n /messagebroker \n /port \n /get_devices \n /get_device_by_ID \n /get_users \n /get_user_by_ID"

        user_input = uri[0]  # search by uri0
        print(f" OPS :{ops}")
        print(operand)
        # Returns to client
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

        else:
            raise NotImplementedError(" Function does not exist yet. ")

    def PUT(self, **params):
        body = cherrypy.request.body.read()
        json_body = json.loads(body.decode('utf-8'))
        ops = list(json_body.values())
        command = list(json_body.values())[0]
        response = " "

        print(f" JSON BODY : {list(json_body.values())} \n OPS : {ops} \n COMMAND : {command}")

        
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

    def addDevice(self, ops):
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
        return response


            
# Not part of catalog class
if __name__ == '__main__':
    
    #Server stuff
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on': True
        }
    }
    cherrypy.server.socket_host = '0.0.0.0' ## Needed for acess (?)
    cherrypy.tree.mount(Catalog(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
