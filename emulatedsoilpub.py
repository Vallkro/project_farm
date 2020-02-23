from simplepub import Simplepub
from simplesub import MySubscriber
import time
import threading
import math

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

soildry=1
# Start value
soilmoist=0.1
freq=2



deviceID = "soilemulator"
mqtt_topic = "sensors"
restServer = "http://localhost:8080"
broker='mqtt.eclipse.org'
tempsub=MySubscriber(deviceID,mqtt_topic+"/temperature",broker)
tempsub.start()
humsub=MySubscriber(deviceID,mqtt_topic+"/humidity",broker)
humsub.start()
flowsub=MySubscriber(deviceID,"watering_topic",broker)
flowsub.start()

def publishnewdata():
    global soilmoist
    # When true, run this function every freq seconds
    threading.Timer(freq,publishnewdata).start()
    #Air humidity
    #qa=humsub.lastmessage.payload
    qa=0.1
    #wind velo assume const if indoors
    u=0.1
    #Temp
    Ts=20
    #Ts=tempsub.lastmessage.payload
    #flow
    try:
        flow=flowsub.lastmessage.payload
    except AttributeError:
            flow="no_flow"
            
    Q=0
    if flow=="no_flow":
        Q=0
    elif flow=="low_flow":
        Q=0.001 #M^3/s

    elif flow=="high_flow":
        Q=0.002

    #Specific humidity
    h=math.exp(psi*g/(Rw*Ts))
    #Evap rate
    E=pAir*Ce*u*(h-qa)

    #Calc soil humidity
    soilmoist=soilmoist+Q*freq -E*freq
    moist=soilmoist/(soildry+soilmoist)
    print(moist)


publishnewdata()

    


