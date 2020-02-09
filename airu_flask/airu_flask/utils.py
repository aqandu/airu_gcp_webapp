from datetime import datetime, timedelta
import pytz
import utm


def applyCorrectionFactor(factors, data_timestamp, data):
    for factor in factors:
        factor_start = factor['start_date']
        factor_end = factor['end_date']
        if factor_start <= data_timestamp and factor_end > data_timestamp:
            return data*factor['sensor_1003_slope'] + factor['sensor_1003_intercept']
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
        datum['utm_x'], datum['utm_y'], zone_num, zone_let = latlonToUTM(datum['lat'], datum['lon'])
        provided_utm_zones.add(zone_num)

    if len(provided_utm_zones) is not 1:
        raise ValueError('The Provided data must fall into the same UTM zone but it does not!')
