import pymysql
import pandas as pd
import logging
import traceback

logger = logging.getLogger(__name__)

TABLE_CANDLE_PATTERN = "CREATE TABLE IF NOT EXISTS {table}(" \
                       " id int(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, " \
                       " time DATETIME UNIQUE," \
                       " open FLOAT NOT NULL," \
                       " high FLOAT," \
                       " low FLOAT," \
                       " close FLOAT NOT NULL," \
                       " volume_to FLOAT," \
                       " volume_from FLOAT)"


class OneHourCandleDB(object):

    def __init__(self):
        pass

    @staticmethod
    def get_connection():
        try:
            connection = pymysql.connect(host='127.0.0.1',
                                         user='root',
                                         password='12345',
                                         db='hourly_ohlc',
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor,
                                         autocommit=True)
            return connection
        except pymysql.Error as e:
            logger.exception(str(e))
            print(traceback.print_exc())

    def create_candle_table(self, asset):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                query = TABLE_CANDLE_PATTERN.replace('{table}', asset)
                cursor.execute(query)

                if cursor.description:
                    logger.info(cursor.description)

        finally:
            connection.close()

    def does_table_exist(self, table):
        connection = self.get_connection()
        try:
            with connection.cursor(pymysql.cursors.SSCursor) as cursor:
                query = "SHOW TABLES"
                cursor.execute(query)
                tables_in_db = cursor.fetchall()

                for table_in_db in tables_in_db:
                    if table == table_in_db[0]:
                        return True

                return False
        finally:
            if connection:
                connection.close()

    def insert_many_candles(self, table, candles):
        self.create_candle_table(table)
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = "INSERT IGNORE INTO " + table + "(time, open, high, low, close, volume_to, volume_from)" \
                                                        " VALUES(FROM_UNIXTIME(%s),%s,%s,%s,%s,%s,%s)"
                cursor.execute("SET time_zone='+00:00'")
                cursor.executemany(query, candles)

                if cursor.description:
                    logger.info(cursor.description)

                return cursor.rowcount

        finally:
            if connection:
                connection.close()

    def get_last_candle(self, table):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = "SELECT time FROM " + table + " ORDER BY time DESC LIMIT 1"

                cursor.execute(query)
                fetched_data = cursor.fetchone()

                if fetched_data:
                    return fetched_data['time']

        finally:
            if connection:
                connection.close()

    def aggregate_candles(self, candles, aggregate):
        idx = 0
        res_candles = []

        while True:
            try:
                open_time = candles[idx]['time']

                if open_time.hour % aggregate == 0:
                    open_price = candles[idx]['open']
                    close_price = candles[idx + aggregate - 1]['close']
                    highest_price = candles[idx]['high']
                    lowest_price = candles[idx]['low']
                    total_volume_to = candles[idx]['volume_to']
                    total_volume_from = candles[idx]['volume_from'] if candles[idx]['volume_from'] else 0

                    for i in range(idx + 1, idx + aggregate):
                        if candles[i]['low'] < lowest_price:
                            lowest_price = candles[i]['low']

                        if candles[i]['high'] > highest_price:
                            highest_price = candles[i]['high']

                        total_volume_to = total_volume_to + candles[i]['volume_to']
                        total_volume_from = total_volume_from + candles[i]['volume_from'] if candles[i][
                            'volume_from'] else 0

                    res_candles.append({
                        'open': open_price,
                        'close': close_price,
                        'high': highest_price,
                        'low': lowest_price,
                        'volume_to': total_volume_to,
                        'volume_from': total_volume_from,
                        'time': open_time
                    })

                    idx = idx + aggregate
                else:
                    idx = idx + 1

            except IndexError as e:
                break

        return res_candles

    def get_all_candles_between(self, table, start_dtm, end_dtm, aggregate=1):
        connection = self.get_connection()

        try:
            with connection.cursor() as cursor:
                query = "SELECT time, open, high, low, close, volume_from, volume_to " \
                        "FROM " + table + " WHERE time BETWEEN %s AND %s ORDER BY time ASC"

                cursor.execute(query, (start_dtm, end_dtm))

                candles = cursor.fetchall()

                if candles:
                    aggregated_candles = self.aggregate_candles(candles, aggregate)

                    df = pd.DataFrame(aggregated_candles)
                    df.rename(columns={'time': 'T',
                                       'open': 'O',
                                       'high': 'H',
                                       'low': 'L',
                                       'close': 'C',
                                       'volume_from': 'V',
                                       'volume_to': 'QV',
                                       },
                              inplace=True)
                    return df
        finally:
            if connection:
                connection.close()
