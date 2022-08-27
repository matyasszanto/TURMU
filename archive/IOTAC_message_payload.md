#### IoTAC Message Formats Document - TURMU

###### Tecnalia R&I
###### Author:leonardo.gonzalez@tecnalia.com

- Document Version: 0.1
- Date: June 10, 2020

#### MQTT Topic Format

- Format vehicles: `iotac/<vehicle-id>/<attribute>`
- Format central planner: iotac/<central-planner-id>/<attribute>
- `<vehicle-id>` is unique to each vehicle in IoTAC
- `<central-planner-id>` TBD
- `<attribute>` is the attribute whose details are being dispatched in the message.

#### The available values of vehicle ATTRIBUTES are:

- egovehicle
- obstacle
- platoon_status
- vehicle_status
- platoon_formation

#### Payload Formats

1.  Attribute Type: egovehicle

    - MQTT Topic Name: `iotac/<vehicle-id>/egovehicle`
    - Sample Message:

```
    {
    	"vehicleId" : "<vehicle-id>",
    	"timestamp" : "2021-11-07T13:50:11.326860Z",
    	"latitude" : "59.408259",
    	"longitude" : "17.95298",
        "speed" : "3", // In m/s
        "acceleration" : "1.5", // In m/s2
        "yaw" : "0.0", // In degrees
        "yawRate" : "0.0", //In degrees/s2
        "length": "3", //In meters
        "width": "1.8" //In meters
    }
```

2.  Attribute Type: obstacle

    - MQTT Topic Name: `iotac/<vehicle-id>/obstacle`
    - Sample Message:

```
    {
        "obstacleId" : "<obstacle-id>",
        "timestamp" : "2021-11-07T13:50:11.326860Z",
        "type" : "3",
        "latitude" : "59.408259",
        "longitude" : "17.95298",
        "speed" : "3", // In m/s
        "length": "3", //In meters
        "width": "1.8" //In meters
    }
```

3.  Attribute Type: platoon_status

    - MQTT Topic Name: `iotac/<vehicle-id>/platoon_status`
    - Sample Message:

```
    {
    	"id" : "<id>", @Carlos??
        "timestamp" : "2021-11-07T13:50:11.326860Z",
    	"referenceSpeed" : "2.5", //in m/s
        "referenceACC" : "2.5", //in m/s
        "joinRequest" : "True",
        "joinResponse" : "False" ,
        "platoonId" : "15",
        "leaveRequest" : "False",
        "platoonPosition" : "2" 
    }
```

4.  Attribute Type: vehicle_status

    - MQTT Topic Name: `iotac/<vehicle-id>/vehicle_status`
    - Sample Message:

```
    {   
        "timestamp" : "2021-11-07T13:50:11.326860Z",
    	"lidarStatus" : "False",
        "obuStatus" : "False",
        "actuatorsStatus" : "False",
        "gnssStatus" : "False"
    }
```

5.  Attribute Type: platoon_formation

    - MQTT Topic Name: `iotac/<vehicle-id>/platoon_formation`
    - Sample Message:

```
    {
        "timestamp" : "2021-11-07T13:50:11.326860Z",
    	"platoonFormation" : "True",
    	"platoonDissmiss" : "True",
        "referenceSpeed" : "2.71",
        "goalLat" : "0.7",
        "goalLong" : "2.1" 
        "vehicleCompromised" : "False",
        "vehicleCompromisedId" : "37"
    }
```