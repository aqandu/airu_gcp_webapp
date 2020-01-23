![AirU Logo](/airu_flask/airu_flask/static/data/aqLogo.png)

## AirU Google Cloud Project including API for BigQuery sensor data

#### URL: [scottgale.appspot.com](scottgale.appspot.com)

#### API Endpoints

#### Endpoint: /request_sensor_data

**<u>Description:</u>** Retrieves PM 2.5 sensor data for the specified device for a given number of days in the past referenced from the current day. If days=3, the query will return all the data in the last 3 days. This endpoint provides the flexibility to request data for one sensor, multiple sensors, or all sensors. Data is returned in JSON format. 

**<u>Query parameters:</u>**

**device_id**: required. The device id (usually the MAC address with colons omitted) of the desired sensor data. For multiple devices, separate each device id by a comma. For data on all devices, set device_id=all.

​	*Format*: 12 digit hexadecimal number (12AB34CD56ef) - alpha characters can be upper or lowercase.

**days**: required. The number of days of data to return from the current data.

​	*Format*: Integer

**<u>Examples:</u>**

Example 1: /request_sensor_data?device_id=3C71BF153718&days=1

Example 2: /request_sensor_data?device_id=3C71BF153718,F45EAB9C48E6&days=2

Example 3: /request_sensor_data?device_id=all&days=3



#### Endpoint: /request_model_data

**<u>Description:</u>** Retrieves all sensor data within a given radius of a specified center point and within a given date range. If the date range and / or the radius is large expect this query to take some time. Data is returned in JSON format. 

**<u>Query parameters:</u>**

**lat**: required. Latitude of the center point. 

​	*Format*: Floating point number. 

**lon**: required. Longitude of the center point. Format: Floating point number.

**radius**: required. Specifies the radius from the center point of the query.

​	*Format*: Integer or floating point number. 

**start_date**: required. The start date range of the query.

​	*Format*: YYYY-MM-DD/HH:MM:SS (Example: 2020-01-15/07:30:00)

**end_date**: required. The end date for the query

​	*Format*: YYYY-MM-DD/HH:MM:SS (Example: 2020-01-15/15:30:00)

**<u>Examples:</u>**

Example: /request_model_data?lat=40.6789&lon=-111.8141&radius=1&start_date=2020-01-23/00:00:00&end_date=2020-01-23/10:00:00





​	