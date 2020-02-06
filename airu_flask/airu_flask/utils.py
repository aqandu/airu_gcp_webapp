from datetime import datetime
import pytz


def applyCorrectionFactor(factors, data_timestamp, data):
    for factor in factors:
        factor_start = factor['start_date']
        factor_end = factor['end_date']
        if factor_start <= data_timestamp and factor_end > data_timestamp:
            print('\nUSING FACTOR: ', factor)
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

