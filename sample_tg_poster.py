import threading
import os
from helpers.date_time_helper import *
from helpers.binance_helper import BinanceHelper
from rsi_divergence_finder import *
from telegram_poster import TelegramPoster
from timeframe import TimeFrame
from db.one_hour_candle_db import OneHourCandleDB
import logging
import talib

os.chdir(os.path.dirname(os.path.realpath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message).200s",
    handlers=[
        logging.FileHandler("{0}.log".format("logs")),
        logging.StreamHandler()
    ])

logger = logging.getLogger(__name__)

hourly_db = OneHourCandleDB()


# According the current time, returns timeframes to find divergences from
def get_time_frames_to_check():
    timeframes = []
    utc_now = datetime.utcnow()

    hours = utc_now.hour

    if hours % 4 == 0:
        timeframes.append(TimeFrame.FOUR_HOURS)

    if hours % 6 == 0:
        timeframes.append(TimeFrame.SIX_HOURS)

    if hours % 8 == 0:
        timeframes.append(TimeFrame.EIGHT_HOURS)

    if hours % 12 == 0:
        timeframes.append(TimeFrame.TWELVE_HOURS)

    if hours == 0:
        timeframes.append(TimeFrame.ONE_DAY)

    return timeframes


# Checks if the last inserted candle in database is the most recently closed candle
def is_db_uptodate(db_table):
    try:
        lcandle_open_time_in_db = hourly_db.get_last_candle(db_table)
        return lcandle_open_time_in_db == get_most_recent_ot(60)
    except Exception:
        return False


def find_divergences(time_frames):
    tg_poster = TelegramPoster()
    tg_message_dict = tg_poster.get_empty_msg_dict(time_frames)

    # I am only finding divergences on pairs with BTC or USDT quote assets, so here filtering them out
    all_pairs = [pair for pair in BinanceHelper.get_all_market_pairs() if pair.endswith(('BTC', 'USDT'))]

    logger.info('Going to check %s pairs', len(all_pairs))

    for pair in all_pairs:
        try:
            db_table = "Binance_{}".format(pair)

            if not is_db_uptodate(db_table):
                # Skip the pair if ohlc data is not up to date in DB
                logger.info('%s database is not up-to-date', pair)
                continue

            for tf in time_frames:
                logger.info('Checking %s pair in %s time frame', pair, tf.value[1])

                end_dtm = datetime.utcnow()
                # 91 is the number of candles to get from db
                # Because we need at least 90 (14 + 21 + 55) candles from the past to find divergences
                # 14 - RSI window
                # 21 - Number of most recent candles to skip
                # 55 - Number of candles to go through to compare to current candle
                # These numbers are used in 'get_rsi_divergences' function
                start_dtm = end_dtm - timedelta(hours=int((tf.value[0] / 60) * 91))

                candles_df = hourly_db.get_all_candles_between(db_table,
                                                               start_dtm,
                                                               end_dtm,
                                                               aggregate=int((tf.value[0] / 60)))

                if candles_df is None or len(candles_df) == 0:
                    logger.info('%s candles data is empty', pair)
                    continue

                # Here I am multiplying close price to 10^5, otherwise TA-Lib is giving incorrect rsi
                candles_df[RSI_COLUMN] = talib.RSI(candles_df[BASE_COLUMN] * 100000, timeperiod=14)
                candles_df.dropna(inplace=True)

                divergences = get_rsi_divergences(candles_df,
                                                  tf=tf)

                if len(divergences):
                    logger.info('Got %s divergences for %s pair', len(divergences), pair)
                    dv = divergences[0]
                    tg_message_dict[tf.value[1]][dv['type']].append(pair)
                    # Result Example: message_dict[240]['bullish'] = ['BTCUSDT', 'ETHUSDT'] ->
                    # Bullish divergence is detected in 240 Min (4 hour) time frame in BTCUSDT and ETHUSDT pairs

        except Exception as e:
            logger.exception(str(e))
            continue

    # Post messages for each time frame with the list of pairs that have divergences detected
    for tf in time_frames:
        msg_to_post = tg_poster.get_message_to_post(tg_message_dict, tf)

        if msg_to_post:
            tg_poster.post_msg(msg_to_post)
            time.sleep(3)


if __name__ == '__main__':
    timeframes = get_time_frames_to_check()

    if len(timeframes) > 0:
        divs_thread = threading.Thread(target=find_divergences,
                                       args=(timeframes,))

        divs_thread.start()
    else:
        logging.info('No time frames to check')
