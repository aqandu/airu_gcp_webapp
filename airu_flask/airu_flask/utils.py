from datetime import datetime, timedelta
import pytz
import utm

def removeInvalidSensors(sensor_data):
    # TODO
    # sensor is invalid its average reading for any day exceeds 350 ug/m3

    # 5003 sensors are invalid if Raw 24-hour average PM2.5 levels are > 5 ug/m3 AND the two sensors differ by more than 16%
    # * Otherwise just average the two readings and correct as normal.
    return sensor_data

def applyCorrectionFactor(factors, data_timestamp, data, sensor_type):
    for factor in factors:
        factor_start = factor['start_date']
        factor_end = factor['end_date']
        if factor_start <= data_timestamp and factor_end > data_timestamp:
            if sensor_type == '1003':
                return data*factor['1003_slope'] + factor['1003_intercept']
            elif sensor_type == '3003':
                return data*factor['3003_slope'] + factor['3003_intercept']
            elif sensor_type == '5003':
                return data*factor['5003_slope'] + factor['5003_intercept']
    print('\nNo correction factor found for ', data_timestamp)
    return data


def getScalesInTimeRange(scales, start_time, end_time):
    relevantScales = []
    for scale in scales:
        scale_start = scale['start_date']
        scale_end = scale['end_date']
        if start_time < scale_end and end_time >= scale_start:
            relevantScales.append(scale)
    return relevantScales


def parseDateTimeParameter(datetime_string):
    datetime_string = datetime_string.replace('/', ' ')
    # datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone('US/Mountain'))
    try:
        return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S%z').astimezone(pytz.timezone('US/Mountain'))
    except:
        try:
            # assume mountain time if no time zone provided
            return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S').astimezone(pytz.timezone('US/Mountain'))
        except:
            return None


def interpolateQueryDates(start_datetime, end_datetime, frequency):
    query_dates = []
    query_date = start_datetime
    while query_date <= end_datetime:
        query_dates.append(query_date)
        query_date = query_date + timedelta(hours=frequency)

    return query_dates


def latlonToUTM(lat, lon):
    return utm.from_latlon(lat, lon)


def convertLatLonToUTM(sensor_data):
    provided_utm_zones = set()
    for datum in sensor_data:
        datum['utm_x'], datum['utm_y'], datum['zone_num'], zone_let = latlonToUTM(datum['lat'], datum['lon'])
    #     provided_utm_zones.add(zone_num)

    # if len(provided_utm_zones) is not 1:
    #     raise ValueError(f'The Provided data must fall into the same UTM zone but it does not! UTM zones provided: {provided_utm_zones}')
