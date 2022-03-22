import requests as rq
from helpers.date_time_helper import *


class TelegramPoster:
    _token = "TG_BOT_TOKEN"
    _url = "https://api.telegram.org/bot"
    _channel_id = "TG_CHANNEL_ID"

    def __init__(self):
        self._url += self._token

    def post_msg(self, text):
        print(text)

        method = self._url + "/sendMessage?chat_id=" + self._channel_id + "&text=" + text + "&parse_mode=html"
        r = rq.post(method)

        return r.status_code
    
    @staticmethod
    def utf8len(s):
        return len(s.encode('utf-8'))

    @staticmethod
    def is_tg_message_sendable(message):
        return TelegramPoster.utf8len(message) < 4096

    @staticmethod
    def get_readable_message_for_pairs(pairs_list, quote_asset):
        # Converting pairs to base assets: [XRPUSDT, ADABTC] -> [XRP, ADA]
        pairs_list = [pair for pair in pairs_list if pair.endswith(quote_asset)]
        base_assets = [pair[:-len(quote_asset)] for pair in pairs_list]

        if len(base_assets) > 0:
            return '• <i>X-{0}:</i> {1}\n'.format(quote_asset, ', '.join(base_assets))
        else:
            return ''

    def get_message_to_post(self, tg_messages_dict, time_frame):
        tf_str = time_frame.value[1]

        close_time = tg_messages_dict[tf_str]['close_time']
        bullish_dvs = tg_messages_dict[tf_str]['bullish']
        h_bullish_dvs = tg_messages_dict[tf_str]['h_bullish']
        bearish_dvs = tg_messages_dict[tf_str]['bearish']
        h_bearish_dvs = tg_messages_dict[tf_str]['h_bearish']
        oversold_rsis = tg_messages_dict[tf_str]['oversold']
        overbought_rsis = tg_messages_dict[tf_str]['overbought']
        bullish_dvs_count = len(bullish_dvs)
        h_bullish_dvs_count = len(h_bullish_dvs)
        bearish_dvs_count = len(bearish_dvs)
        h_bearish_dvs_count = len(h_bearish_dvs)
        bulls_message = ''
        bears_message = ''

        if bullish_dvs_count > 0:
            bulls_message += '<b>{}</b>\n'.format('Bullish Divergences')

            bulls_message += TelegramPoster.get_readable_message_for_pairs(bullish_dvs, 'BTC')
            bulls_message += TelegramPoster.get_readable_message_for_pairs(bullish_dvs, 'USDT')
            bulls_message += '\n'

        if h_bullish_dvs_count > 0:
            bulls_message += '<b>{0}</b>\n'.format('Hidden Bullish Divergences')

            bulls_message += TelegramPoster.get_readable_message_for_pairs(h_bullish_dvs, 'BTC')
            bulls_message += TelegramPoster.get_readable_message_for_pairs(h_bullish_dvs, 'USDT')
            bulls_message += '\n'

        if len(oversold_rsis) > 0:
            bulls_message += '<b>Oversold</b>\n'
            bulls_message += TelegramPoster.get_readable_message_for_pairs(oversold_rsis, 'BTC')
            bulls_message += TelegramPoster.get_readable_message_for_pairs(oversold_rsis, 'USDT')
            bulls_message += '\n'

        if bearish_dvs_count > 0:
            bears_message += '<b>{}</b>\n'.format('Bearish Divergences')

            bears_message += TelegramPoster.get_readable_message_for_pairs(bearish_dvs, 'BTC')
            bears_message += TelegramPoster.get_readable_message_for_pairs(bearish_dvs, 'USDT')
            bears_message += '\n'

        if h_bearish_dvs_count > 0:
            bears_message += '<b>{0}</b>\n'.format('Hidden Bearish Divergences')

            bears_message += TelegramPoster.get_readable_message_for_pairs(h_bearish_dvs, 'BTC')
            bears_message += TelegramPoster.get_readable_message_for_pairs(h_bearish_dvs, 'USDT')
            bears_message += '\n'

        if len(overbought_rsis) > 0:
            bears_message += '<b>Overbought</b>\n'
            bears_message += TelegramPoster.get_readable_message_for_pairs(overbought_rsis, 'BTC')
            bears_message += TelegramPoster.get_readable_message_for_pairs(overbought_rsis, 'USDT')
            bears_message += '\n'

        if bulls_message or bears_message:
            header = '%23{0}\nClose Time: {1}\n'.format(tf_str, close_time)

            if bulls_message:
                bulls_message = "\n<s>{0}</s>\n\n{1}".format(60 * ":", bulls_message)

            if bears_message:
                bears_message = "<s>{0}</s>\n\n{1}".format(60 * ":", bears_message)

            message_to_send = header + bulls_message + bears_message

            if TelegramPoster.is_tg_message_sendable(message_to_send):
                return message_to_send
            else:
                return "Message is too big to send"

    # Construct empty message
    def get_empty_msg_dict(self, time_frames):
        tg_messages_dict = dict()

        for tf in time_frames:
            recent_ot_tim = floor_epoch_n_minutes(int(time.time()), tf.value[0])

            tg_messages_dict[tf.value[1]] = dict()
            tg_messages_dict[tf.value[1]]['bullish'] = []
            tg_messages_dict[tf.value[1]]['h_bullish'] = []
            tg_messages_dict[tf.value[1]]['bearish'] = []
            tg_messages_dict[tf.value[1]]['h_bearish'] = []
            tg_messages_dict[tf.value[1]]['close_time'] = date_time_to_str(from_utc_timestamp_to_utc_dtm(recent_ot_tim),
                                                                           time_format="%Y-%m-%d %H:%M:%S")

        return tg_messages_dict

