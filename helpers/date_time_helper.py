from datetime import datetime, timedelta
from dateutil import tz
import pytz
import calendar
import math
import time

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
SHORT_DATE_TIME_FORMAT_START = "%d %b, %H:%M"
SHORT_TIME_FORMAT_START = "%H:%M"
DATE_TIME_FORMAT = "%d %b,"


def str_to_date_time(date_time_str, from_time_format=TIME_FORMAT):
    return datetime.strptime(date_time_str, from_time_format)


def date_time_to_str(date_time, time_format=TIME_FORMAT):
    return datetime.strftime(date_time, time_format)


def from_utc_str_to_local_dtm(date_time, from_time_format=TIME_FORMAT):
    utc_date_time = datetime.strptime(date_time, from_time_format)
    return from_utc_dtm_to_local_dtm(utc_date_time)


def from_utc_dtm_to_local_dtm(utc_date_time, remove_tz=False):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = utc_date_time.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)

    if remove_tz:
        central = central.replace(tzinfo=None)

    return central


def from_local_dtm_to_utc_dtm(date_time, remove_tz=False):
    local = pytz.timezone("Asia/Seoul")
    local_dt = local.localize(date_time, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)

    if remove_tz:
        utc_dt = utc_dt.replace(tzinfo=None)

    return utc_dt


def from_local_dtm_to_timestamp(local_dtm):
    return time.mktime(local_dtm.timetuple())


def from_utc_str_to_local_str(date_time, from_time_format=TIME_FORMAT, to_time_format=TIME_FORMAT):
    return from_utc_str_to_local_dtm(date_time, from_time_format=from_time_format).strftime(to_time_format)


def from_utc_timestamp_to_local_dtm(date_time):
    return datetime.fromtimestamp(int(date_time))


def from_utc_timestamp_to_local_string(date_time, to_time_format=TIME_FORMAT):
    return from_utc_timestamp_to_local_dtm(date_time).strftime(to_time_format)


def localize_date_time(date_time):
    time_zone = pytz.timezone('Asia/Seoul')
    return time_zone.localize(date_time)


def set_utc_timezone(date_time):
    return pytz.utc.localize(date_time)


def get_n_minutes_before(minutes, start_date_time=None):
    if start_date_time is None:
        start_date_time = datetime.now()

    if minutes != 0:
        return start_date_time - timedelta(minutes=minutes)
    else:
        return start_date_time


def from_utc_timestamp_to_utc_dtm(epoch_time):
    return datetime.utcfromtimestamp(epoch_time)


def from_utc_dtm_to_utc_timestamp(utc_date_time):
    return calendar.timegm(utc_date_time.utctimetuple())


def floor_datetime_n_minutes(tm, minutes):
    return tm - timedelta(minutes=tm.minute % minutes,
                          seconds=tm.second,
                          microseconds=tm.microsecond)


def ceil_datetime_n_seconds(tm, seconds):
    nsecs = tm.minute * 60 + tm.second + tm.microsecond * 1e-6
    delta = math.ceil(nsecs / seconds) * seconds - nsecs
    return tm + timedelta(seconds=delta)


def ceil_datetime_n_minutes(tm, minutes):
    return ceil_datetime_n_seconds(tm, minutes * 60)


def floor_epoch_n_minutes(epoch, minutes):
    return (epoch // (minutes * 60)) * minutes * 60


def ceil_epoch_n_minutes(epoch, minutes):
    return floor_epoch_n_minutes(epoch, minutes) + minutes * 60


def get_date_by_epoch(timestamp):
    epoch = datetime.utcfromtimestamp(0)
    return (from_utc_timestamp_to_utc_dtm(timestamp).replace(hour=0, minute=0, second=0) - epoch).total_seconds()


def round_datetime_n_minutes(tm, minutes):
    discard = timedelta(minutes=tm.minute % minutes,
                        seconds=tm.second,
                        microseconds=tm.microsecond)
    tm -= discard
    if discard >= timedelta(minutes=(minutes / 2)):
        tm += timedelta(minutes=minutes)

    return tm


def get_start_of_day(date_time):
    return date_time.replace(hour=0, minute=0, second=0)


def get_end_of_day(date_time):
    return date_time.replace(hour=23, minute=59, second=59)


def ceil_12_hours(timestamp):
    date_time = from_utc_timestamp_to_utc_dtm(timestamp)
    mid_of_day = date_time.replace(hour=12, minute=0, second=0)
    epoch = datetime.utcfromtimestamp(0)

    if date_time <= mid_of_day:
        return (mid_of_day - epoch).total_seconds()
    else:
        return ((mid_of_day + timedelta(hours=12)) - epoch).total_seconds()


def floor_12_hours(timestamp):
    date_time = from_utc_timestamp_to_utc_dtm(timestamp)
    mid_of_day = date_time.replace(hour=12, minute=0, second=0)
    epoch = datetime.utcfromtimestamp(0)

    if date_time <= mid_of_day:
        return ((mid_of_day - timedelta(hours=12)) - epoch).total_seconds()
    else:
        return (mid_of_day - epoch).total_seconds()


# Returns most recent open time
def get_most_recent_ot(tf_in_minutes):
    recent_ot_tim = floor_epoch_n_minutes(int(time.time()), tf_in_minutes) - tf_in_minutes * 60
    return from_utc_timestamp_to_utc_dtm(recent_ot_tim)