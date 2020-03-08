#!/usr/bin/python3
import requests
cont=True
while cont:
    f=input("Avalible commands : \nport\t-get the port \nmessagebroker\t-get messagebroker \nget_devices\t -get all the registred devices \nget_device_by_ID <ID>\t- get command by ID \nget_users\t-get all users\nget_user_by_ID <ID>\t- get user by id\n")

    print(f"INPUT: {f.split()}")
    CL=f.split()
    #check if valid
    #Option to quit
    if CL[0]=="q":
        cont=False
    else:


        #Build command to server
        getURL='http://localhost:8080/' +CL[0]
        for op in range(1, len(CL)):    
            getURL+='/'+str(CL[op])

        print(f"GETURL: <{getURL}>")

        response=requests.get(getURL)
        print(f"RESPONSE :<{response.text}>")
