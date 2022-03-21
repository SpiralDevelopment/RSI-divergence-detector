import math
import numpy as np


def calculate_hypotenuse(adjacent, opposite):
    return math.sqrt(adjacent**2 + opposite**2)


def get_cur_value_from_linear_function(x1, y1, x2, y2, cur_x):
    b = (y1 - y2) / (x1 - x2)
    return y1 + b * (cur_x - x1)


def does_point_cross_up_line(l_x1, l_y1, l_x2, l_y2, x, y, diff=1):
    cur_value = get_cur_value_from_linear_function(l_x1, l_y1, l_x2, l_y2, x)
    diff_now = y / cur_value

    return diff_now > diff


def does_point_cross_down_line(l_x1, l_y1, l_x2, l_y2, x, y, diff=1):
    cur_value = get_cur_value_from_linear_function(l_x1, l_y1, l_x2, l_y2, x)
    diff_now = cur_value / y
    return diff_now > diff


def does_any_value_cross_down(rsi_candles_df, start_rsi, start_time, end_rsi, end_time, value_column='C_rsi',
                              diff=1):
    candles_between = rsi_candles_df[(rsi_candles_df['T'] > start_time) & (rsi_candles_df['T'] < end_time)]

    start_time = (start_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    end_time = (end_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

    for index, row in candles_between.iterrows():
        res = does_point_cross_down_line(start_time,
                                         start_rsi,
                                         end_time,
                                         end_rsi,
                                         (row['T'] - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'),
                                         row[value_column],
                                         diff=diff)

        if res:
            return res

    return False


def does_any_value_cross_up(rsi_candles_df, start_rsi, start_time, end_rsi, end_time, value_column='C_rsi', diff=1):
    candles_between = rsi_candles_df[(rsi_candles_df['T'] > start_time) & (rsi_candles_df['T'] < end_time)]

    start_time = (start_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    end_time = (end_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

    for index, row in candles_between.iterrows():
        res = does_point_cross_up_line(start_time,
                                       start_rsi,
                                       end_time,
                                       end_rsi,
                                       (row['T'] - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'),
                                       row[value_column],
                                       diff=diff)

        if res:
            return res

    return False


def get_angle(start_rsi, start_time, end_rsi, end_time, tf=None):
    start_time = (start_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    end_time = (end_time - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

    opposite = abs(end_rsi - start_rsi)
    adjacent = abs(end_time - start_time) / (60 * 60)

    if tf:
        adjacent = adjacent / (tf.value[0] / 60.0)

    angle = np.rad2deg(np.arctan2(opposite, adjacent))

    return angle
