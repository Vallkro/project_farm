from simplepub import Simplepub
from simplesub import MySubscriber
import time
import threading
import math
import requests

#soil emulation
#Params
humidity=0.1
temperature=20
#Bulk transfer coefficient
Ce=0.003
#Air density
pAir=1.225
#Gas const water vapor
Rw=8.314
#Gravity
g=9.82
#Soil water potential
psi=-0.05
#Specific humidity
q=3.5/100000

soildry=40
# Start value
soilmoist=20
freq=2


home="polito/01QWRBH/SmartFarm/"
deviceID = "device1/"
mqtt_topic = "sensors"
restServer = "http://localhost:8080"
broker='mqtt.eclipse.org'
port=1883
tempsub=MySubscriber(deviceID,"polito/01QWRBH/SmartFarm/device1/sensors/temperature",broker)
tempsub.start()
humsub=MySubscriber(deviceID,"polito/01QWRBH/SmartFarm/device1/sensors/humidity",broker)
humsub.start()
flowsub=MySubscriber(deviceID,"polito/01QWRBH/SmartFarm/device1/outputs/waterflow",broker)
flowsub.start()
pub=Simplepub(deviceID,broker,port)



def publishnewdata():
    global soilmoist
    # When true, run this function every freq seconds
    threading.Timer(freq,publishnewdata).start()
    #Air humidity
    qa=float(humsub.lastmessage.payload)
    #qa=0.1
    #wind velo assume const if indoors
    u=0.1
    #Temp
    #Ts=20
    Ts=float(tempsub.lastmessage.payload)
    #flow
    try:
        flow=flowsub.lastmessage.payload
    except AttributeError:
            flow="no_flow"
    Q=0
    if flow != "no_flow":
        Q=float(flowsub.lastmessage.payload)      
    
    #Specific humidity
    h=math.exp(psi*g/(Rw*Ts))
    #Evap rate
    E=pAir*Ce*u*(h-qa)

    #Calc soil humidity
    soilmoist=soilmoist+Q*freq +E*freq
    moist=soilmoist/(soildry+soilmoist)
    if moist<0:
        moist=0

    pub.publish("polito/01QWRBH/SmartFarm/device1/sensors/soilhumidity",round(moist,3))
    

pub.start()
publishnewdata()

    
#Publihsing topic sensors/soilhumidity
#listens to topic watering_topic 
#and values no_flow, low_flow, high_flow

