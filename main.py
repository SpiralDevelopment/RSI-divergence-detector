from binance_helper import BinanceHelper
from trading_helper import *
from telegram_poster import TelegramPoster
import logging
from timeframe import TimeFrame
import threading
from one_hour_candle_db import OneHourCandleDB
import os
from helper import *

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
hourly_db = OneHourCandleDB()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message).200s",
    handlers=[
        logging.FileHandler("{0}.log".format("logs")),
        logging.StreamHandler()
    ])

logger = logging.getLogger(__name__)
tg_poster = TelegramPoster()


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
def is_db_uptodate(pair):
    try:
        lcandle_open_time_in_db = hourly_db.get_last_candle("Binance_{}".format(pair))
        return lcandle_open_time_in_db == get_recent_ot(60)
    except Exception:
        return False


def analyze_pairs(time_frames):
    message_dict = get_empty_msg_dict(time_frames)

    # I am only finding divergences on pairs with BTC or USDT quote assets, so here filtering them out
    all_pairs = [pair for pair in BinanceHelper.get_all_market_pairs() if pair.endswith(('BTC', 'USDT'))]

    logger.info('Going to check %s pairs', len(all_pairs))

    for pair in all_pairs:
        try:
            if not is_db_uptodate(pair):
                # Skip the pair if ohlc data is not up to date in DB
                logger.info('%s database is not up-to-date', pair)
                continue

            for tf in time_frames:
                logger.info('Checking %s pair in %s time frame', pair, tf.value[1])

                end_dtm = datetime.utcnow()
                # 111 is the number of candles to get from db
                start_dtm = end_dtm - timedelta(hours=int((tf.value[0] / 60) * 111))
                table = "Binance_{}".format(pair)

                candles_df = hourly_db.get_all_candles_between(table,
                                                               start_dtm,
                                                               end_dtm,
                                                               aggregate=int((tf.value[0] / 60)))

                if candles_df is None or len(candles_df) == 0:
                    logger.info('%s candles data frame retrieved form DB is empty', pair)
                    continue

                divergences = get_divergences(candles_df,
                                              tf=tf)

                if len(divergences):
                    logger.info('Got %s divergences for %s pair', len(divergences), pair)
                    dv = divergences[0]
                    message_dict[tf.value[1]][dv['type']].append(pair)
                    # Result Example: message_dict[60]['bullish'] = ['BTCUSDT', 'ETHUSDT'] ->
                    # Bullish divergence is detected in 60 Min (1 hour) time frame in BTCUSDT and ETHUSDT pairs

        except Exception as e:
            logger.exception(str(e))
            continue

    # Post messages for each time frame to telegram with the list of pairs that have divergences detected
    for tf in time_frames:
        msg_to_post = get_message_to_post(message_dict, tf)

        if msg_to_post:
            tg_poster.post_msg(msg_to_post)
            time.sleep(3)


if __name__ == '__main__':
    tfs_to_check = get_time_frames_to_check()

    if len(tfs_to_check) > 0:
        divs_thread = threading.Thread(target=analyze_pairs,
                                       args=(tfs_to_check,))

        divs_thread.start()
    else:
        logging.info('No time frames to check')
