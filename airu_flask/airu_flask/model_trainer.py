
import json
import gaussian_model_utils as model_utils
from datetime import datetime
import pytz


def parseDateTimeParameter(datetime_string):
    datetime_string = datetime_string.replace('/', ' ')
    try:
        return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S%z').astimezone(pytz.timezone('US/Mountain'))
    except:
        try:
            # assume mountain time if no time zone provided
            return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone('US/Mountain'))
        except:
            return None

filename = '2019-11-01_2020-02-28.txt'
with open(filename) as json_file:
    sensor_data = json.load(json_file)

# parse date_time field into datetime objects
for datum in sensor_data:
    datum['date_time'] = parseDateTimeParameter(datum['date_time'])

unique_sensors = {datum['device_id'] for datum in sensor_data}
print(f'Loaded {len(sensor_data)} data points for {len(unique_sensors)} unique devices from file system.')
print(f'Keys: {list(sensor_data[0].keys())}')
print(f'Example datapoint: {sensor_data[0]}')

default_latlon_length_scale = 4300
default_elevation_length_scale = 30
default_time_length_scale = 0.25

model, time_offset = model_utils.createModel(sensor_data, default_latlon_length_scale, default_elevation_length_scale, default_time_length_scale)

latlon_length_scale, elevation_length_scale, time_length_scale = model.getLengthScales()
print(f'before training scales: latlon {latlon_length_scale}, elev {elevation_length_scale}, time {time_length_scale}')
model.train_adam(5,0.1)    #optimize hyperparameter using adam optimizer
latlon_length_scale, elevation_length_scale, time_length_scale = model.getLengthScales()
print(f'after training scales: latlon {latlon_length_scale}, elev {elevation_length_scale}, time {time_length_scale}')
