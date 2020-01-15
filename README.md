![AirU Logo](airu_flask\airu_flask\static\data\aqLogo.png)

 # airu_gcp_webapp

AirU GCP project including API for Big Query

##### URL: scottgale.appspot.com

API Endpoints

#### Endpoint: /request_sensor_data

-  **Query parameters:**

   device_id: required. Specifies the device id (usually the MAC address with colons omitted) of the desired sensor data. For multiple devices, separate each device id by a comma. For data on all devices, set device_id=all.

   days: required. Specifies the number of days of data to return from the current data.

-  Examples:

   Example 1: /request_sensor_data?device_id=3C71BF153718&days=1

   Example 2: /request_sensor_data?device_id=3C71BF153718,F45EAB9C48E6&days=1

   Example 3: /request_sensor_data?device_id=all&days=1







​	