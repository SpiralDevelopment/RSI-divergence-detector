import pandas as pd
from helpers.calculus_helper import *
import logging
from datetime import datetime
from scipy import stats

logger = logging.getLogger(__name__)
RSI_COLUMN = 'rsi'
BASE_COLUMN = 'C'
TIME_COLUMN = 'T'
ANGLE_LIMIT = 45.0  # Limit for angle of divergence lines


def calc_percentage_increase(original, new):
    increase = (new - original) / original
    return increase * 100


# cur_candle_idx - index of the candle to which we compare candles in the past to find divergences
def get_rsi_divergences(df, tf, cur_candle_idx=-1):
    divergences = []

    cur_candle = df.iloc[cur_candle_idx]
    cur_rsi_change = calc_percentage_increase(df.iloc[-2][RSI_COLUMN],
                                              cur_candle[RSI_COLUMN])

    # 'cur_base_value' is the close price here
    cur_base_value_time = cur_candle[TIME_COLUMN]
    cur_base_value = cur_candle[BASE_COLUMN]
    cur_base_value_rsi = cur_candle[RSI_COLUMN]

    # 'candles_to_compare' - Candles in the past to which we compare 'cur_candle' and look for divergences
    # We skip the most recent 21 candles because divergence signals formed among 21 (or less) candles are not that strong
    # We get the other 55 candles before that
    candles_to_compare = df[df[TIME_COLUMN] < cur_base_value_time - pd.Timedelta(minutes=tf.value[0] * 21)]
    candles_to_compare = candles_to_compare.tail(55)
    candles_to_compare_len = candles_to_compare.shape[0]

    if candles_to_compare is None:
        return divergences

    # The rest is RSI divergence detection part
    # Some things are hardcoded there, those are the numbers that I find to be more accurate
    # Feel free to play around with those numbers

    # In the following block, we check if there is bullish divergence
    if cur_base_value_rsi <= 37 and cur_rsi_change < 0:
        bullish_divs = pd.DataFrame()

        for idx, (past_candle_idx, past_candle) in enumerate(candles_to_compare.iterrows()):
            try:
                past_base_value = past_candle[BASE_COLUMN]
                past_base_value_rsi = past_candle[RSI_COLUMN]
                past_base_value_time = past_candle[TIME_COLUMN]

                if past_base_value_rsi > 32:
                    continue

                is_bullish = False

                base_value_change = calc_percentage_increase(past_base_value,
                                                             cur_base_value)
                rsi_change = calc_percentage_increase(past_base_value_rsi,
                                                      cur_base_value_rsi)

                df_in_period = df[(past_base_value_time <= df[TIME_COLUMN]) & (df[TIME_COLUMN] <= cur_base_value_time)]
                seconds = (df_in_period[TIME_COLUMN] - datetime(1970, 1, 1)).dt.total_seconds()
                slope, intercept, r_value, p_value, std_err = stats.linregress(seconds,
                                                                               df_in_period[
                                                                                   BASE_COLUMN])

                if rsi_change >= 6 and base_value_change <= 0 and slope < 0 and pow(r_value, 2) > 0.3:
                    is_bullish = True

                if is_bullish \
                        and does_any_value_cross_down(df,
                                                      past_base_value_rsi,
                                                      past_base_value_time,
                                                      cur_base_value_rsi,
                                                      cur_base_value_time,
                                                      diff=1.05,
                                                      value_column=RSI_COLUMN) is False \
                        and does_any_value_cross_down(df,
                                                      past_base_value,
                                                      past_base_value_time,
                                                      cur_base_value,
                                                      cur_base_value_time,
                                                      diff=1.03,
                                                      value_column=BASE_COLUMN) is False \
                        and get_angle(
                    past_base_value_rsi,
                    past_base_value_time,
                    cur_base_value_rsi,
                    cur_base_value_time,
                    tf=tf) <= ANGLE_LIMIT:
                    bullish_divs = bullish_divs.append(past_candle)
            except Exception as e:
                logging.exception(str(e))

        for index, div in bullish_divs.iterrows():
            divergences.append({'start_dtm': div[TIME_COLUMN],
                                'end_dtm': cur_base_value_time,
                                'rsi_start': div[RSI_COLUMN],
                                'rsi_end': cur_base_value_rsi,
                                'price_start': div[BASE_COLUMN],
                                'price_end': cur_base_value,
                                'type': 'bullish'})
    # In the following block, we check if there is bearish divergence
    elif cur_base_value_rsi >= 63 and 0 < cur_rsi_change:
        bearish_divs = pd.DataFrame()

        for idx, (past_candle_idx, past_candle) in enumerate(candles_to_compare.iterrows()):
            try:
                past_base_value_rsi = past_candle[RSI_COLUMN]

                if past_base_value_rsi < 68:
                    continue

                past_base_value = past_candle[BASE_COLUMN]
                past_base_value_time = past_candle[TIME_COLUMN]
                is_bearish = False

                base_value_change = calc_percentage_increase(past_base_value,
                                                             cur_base_value)
                rsi_change = calc_percentage_increase(past_base_value_rsi, cur_base_value_rsi)

                df_in_period = df[(past_base_value_time <= df[TIME_COLUMN]) & (df[TIME_COLUMN] <= cur_base_value_time)]
                seconds = (df_in_period[TIME_COLUMN] - datetime(1970, 1, 1)).dt.total_seconds()
                slope, intercept, r_value, p_value, std_err = stats.linregress(seconds,
                                                                               df_in_period[
                                                                                   BASE_COLUMN])

                if rsi_change <= -6 and 0 <= base_value_change and slope > 0 and pow(r_value, 2) > 0.3:
                    is_bearish = True

                if is_bearish \
                        and does_any_value_cross_up(df,
                                                    past_base_value_rsi,
                                                    past_base_value_time,
                                                    cur_base_value_rsi,
                                                    cur_base_value_time,
                                                    diff=1.05,
                                                    value_column=RSI_COLUMN) is False \
                        and does_any_value_cross_up(df,
                                                    past_base_value,
                                                    past_base_value_time,
                                                    cur_base_value,
                                                    cur_base_value_time,
                                                    diff=1.03,
                                                    value_column=BASE_COLUMN) is False \
                        and get_angle(
                    past_base_value_rsi,
                    past_base_value_time,
                    cur_base_value_rsi,
                    cur_base_value_time, tf=tf) <= ANGLE_LIMIT:
                    bearish_divs = bearish_divs.append(past_candle)

            except Exception as e:
                logging.exception(str(e))

        for index, div in bearish_divs.iterrows():
            divergences.append({'start_dtm': div[TIME_COLUMN],
                                'end_dtm': cur_base_value_time,
                                'rsi_start': div[RSI_COLUMN],
                                'rsi_end': cur_base_value_rsi,
                                'price_start': div[BASE_COLUMN],
                                'price_end': cur_base_value,
                                'type': 'bearish'})
    # In the following block, we check if there is hidden bearish divergence
    if 50 < cur_base_value_rsi <= 70 and cur_rsi_change > 0:
        h_bearish_divs = pd.DataFrame()

        for idx_lcl, (past_candle_idx, past_candle) in enumerate(candles_to_compare.iterrows()):
            try:
                if idx_lcl in [0, candles_to_compare_len - 1]:
                    continue

                past_base_value = past_candle[BASE_COLUMN]
                past_base_value_rsi = past_candle[RSI_COLUMN]

                if candles_to_compare.iloc[idx_lcl - 1][RSI_COLUMN] < \
                        past_base_value_rsi > \
                        candles_to_compare.iloc[idx_lcl + 1][RSI_COLUMN]:
                    if not (50 < past_base_value_rsi < 65):
                        continue

                    past_base_value_time = past_candle[TIME_COLUMN]
                    is_bearish = False

                    base_value_change = calc_percentage_increase(past_base_value,
                                                                 cur_base_value)
                    rsi_change = calc_percentage_increase(past_base_value_rsi,
                                                          cur_base_value_rsi)

                    df_in_period = df[
                        (past_base_value_time <= df[TIME_COLUMN]) & (df[TIME_COLUMN] <= cur_base_value_time)]
                    seconds = (df_in_period[TIME_COLUMN] - datetime(1970, 1, 1)).dt.total_seconds()
                    slope, intercept, r_value, p_value, std_err = stats.linregress(seconds,
                                                                                   df_in_period[BASE_COLUMN])

                    slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(seconds,
                                                                                        df_in_period[
                                                                                            RSI_COLUMN])

                    if rsi_change >= 6 and base_value_change < 0 and slope < 0 < slope2 and pow(r_value, 2) > 0.3:
                        is_bearish = True

                    if is_bearish \
                            and does_any_value_cross_up(df,
                                                        past_base_value_rsi,
                                                        past_base_value_time,
                                                        cur_base_value_rsi,
                                                        cur_base_value_time,
                                                        diff=1.05,
                                                        value_column=RSI_COLUMN) is False \
                            and does_any_value_cross_up(df,
                                                        past_base_value,
                                                        past_base_value_time,
                                                        cur_base_value,
                                                        cur_base_value_time,
                                                        diff=1.03,
                                                        value_column=BASE_COLUMN) is False \
                            and get_angle(
                        past_base_value_rsi,
                        past_base_value_time,
                        cur_base_value_rsi,
                        cur_base_value_time, tf=tf) <= ANGLE_LIMIT:
                        h_bearish_divs = h_bearish_divs.append(past_candle)
            except Exception as e:
                logging.exception(str(e))
                continue

        for index, div in h_bearish_divs.iterrows():
            divergences.append({'start_dtm': div[TIME_COLUMN],
                                'end_dtm': cur_base_value_time,
                                'rsi_start': div[RSI_COLUMN],
                                'rsi_end': cur_base_value_rsi,
                                'price_start': div[BASE_COLUMN],
                                'price_end': cur_base_value,
                                'type': 'h_bearish'})
    # In the following block, we check if there is hidden bullish divergence
    elif 30 < cur_base_value_rsi <= 50 and cur_rsi_change < 0:
        h_bullish_divs = pd.DataFrame()

        for idx_lcl, (past_candle_idx, past_candle) in enumerate(candles_to_compare.iterrows()):
            try:
                if idx_lcl in [0, candles_to_compare_len - 1]:
                    continue

                past_base_value = past_candle[BASE_COLUMN]
                past_base_value_rsi = past_candle[RSI_COLUMN]

                if candles_to_compare.iloc[idx_lcl - 1][RSI_COLUMN] > \
                        past_base_value_rsi < \
                        candles_to_compare.iloc[idx_lcl + 1][RSI_COLUMN]:
                    if not (40 < past_base_value_rsi < 55):
                        continue

                    past_base_value_time = past_candle[TIME_COLUMN]
                    is_bullish = False

                    base_value_change = calc_percentage_increase(past_base_value,
                                                                 cur_base_value)
                    rsi_change = calc_percentage_increase(past_base_value_rsi,
                                                          cur_base_value_rsi)

                    df_in_period = df[
                        (past_base_value_time <= df[TIME_COLUMN]) & (df[TIME_COLUMN] <= cur_base_value_time)]
                    seconds = (df_in_period[TIME_COLUMN] - datetime(1970, 1, 1)).dt.total_seconds()
                    slope, intercept, r_value, p_value, std_err = stats.linregress(seconds,
                                                                                   df_in_period[BASE_COLUMN])

                    slope2, intercept2, r_value2, p_value2, std_err2 = stats.linregress(seconds,
                                                                                        df_in_period[RSI_COLUMN])

                    if rsi_change <= -6 and 0 < base_value_change and slope > 0 > slope2 and pow(r_value,
                                                                                                 2) > 0.3:
                        is_bullish = True

                    if is_bullish \
                            and does_any_value_cross_down(df,
                                                          past_base_value_rsi,
                                                          past_base_value_time,
                                                          cur_base_value_rsi,
                                                          cur_base_value_time,
                                                          diff=1.05,
                                                          value_column=RSI_COLUMN) is False \
                            and does_any_value_cross_down(df,
                                                          past_base_value,
                                                          past_base_value_time,
                                                          cur_base_value,
                                                          cur_base_value_time,
                                                          diff=1.03,
                                                          value_column=BASE_COLUMN) is False \
                            and get_angle(
                        past_base_value_rsi,
                        past_base_value_time,
                        cur_base_value_rsi,
                        cur_base_value_time, tf=tf) <= ANGLE_LIMIT:
                        h_bullish_divs = h_bullish_divs.append(past_candle)
            except Exception as e:
                logging.exception(str(e))
                continue

        for index, div in h_bullish_divs.iterrows():
            divergences.append({'start_dtm': div[TIME_COLUMN],
                                'end_dtm': cur_base_value_time,
                                'rsi_start': div[RSI_COLUMN],
                                'rsi_end': cur_base_value_rsi,
                                'price_start': div[BASE_COLUMN],
                                'price_end': cur_base_value,
                                'type': 'h_bullish'})

    return divergences


def get_all_rsi_divergences(df, tf):
    all_divergences = []

    for idx in range(df.shape[0]):
        all_divergences += get_rsi_divergences(df, tf, idx)

    return all_divergences
