from date_time_helper import *


def utf8len(s):
    return len(s.encode('utf-8'))


def is_tg_message_sendable(message):
    return utf8len(message) < 4096


def pair_list_to_base_asset_list(pairs_list, quote_asset):
    pairs_list = [pair for pair in pairs_list if pair.endswith(quote_asset)]
    base_assets_list = [pair[:-len(quote_asset)] for pair in pairs_list]

    return base_assets_list


def get_readable_message_for_pairs(pairs_list, quote_asset):
    assets = pair_list_to_base_asset_list(pairs_list, quote_asset)

    if len(assets) > 0:
        return '• <i>X-{0}:</i> {1}\n'.format(quote_asset, ', '.join(assets))
    else:
        return ''


def get_message_to_post(tg_messages_dict, time_frame):
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

        bulls_message += get_readable_message_for_pairs(bullish_dvs, 'BTC')
        bulls_message += get_readable_message_for_pairs(bullish_dvs, 'USDT')
        bulls_message += '\n'

    if h_bullish_dvs_count > 0:
        bulls_message += '<b>{0}</b>\n'.format('Hidden Bullish Divergences')

        bulls_message += get_readable_message_for_pairs(h_bullish_dvs, 'BTC')
        bulls_message += get_readable_message_for_pairs(h_bullish_dvs, 'USDT')
        bulls_message += '\n'

    if len(oversold_rsis) > 0:
        bulls_message += '<b>Oversold</b>\n'
        bulls_message += get_readable_message_for_pairs(oversold_rsis, 'BTC')
        bulls_message += get_readable_message_for_pairs(oversold_rsis, 'USDT')
        bulls_message += '\n'

    if bearish_dvs_count > 0:
        bears_message += '<b>{}</b>\n'.format('Bearish Divergences')

        bears_message += get_readable_message_for_pairs(bearish_dvs, 'BTC')
        bears_message += get_readable_message_for_pairs(bearish_dvs, 'USDT')
        bears_message += '\n'

    if h_bearish_dvs_count > 0:
        bears_message += '<b>{0}</b>\n'.format('Hidden Bearish Divergences')

        bears_message += get_readable_message_for_pairs(h_bearish_dvs, 'BTC')
        bears_message += get_readable_message_for_pairs(h_bearish_dvs, 'USDT')
        bears_message += '\n'

    if len(overbought_rsis) > 0:
        bears_message += '<b>Overbought</b>\n'
        bears_message += get_readable_message_for_pairs(overbought_rsis, 'BTC')
        bears_message += get_readable_message_for_pairs(overbought_rsis, 'USDT')
        bears_message += '\n'

    if bulls_message or bears_message:
        header = '%23{0}\nClose Time: {1}\n'.format(tf_str, close_time)

        if bulls_message:
            bulls_message = "\n<s>{0}</s>\n\n{1}".format(60 * ":", bulls_message)

        if bears_message:
            bears_message = "<s>{0}</s>\n\n{1}".format(60 * ":", bears_message)

        message_to_send = header + bulls_message + bears_message

        if is_tg_message_sendable(message_to_send):
            return message_to_send
        else:
            return "Message is too big to send"


# Returns most recent open time
def get_recent_ot(tf_in_minutes):
    recent_ot_tim = floor_epoch_n_minutes(int(time.time()), tf_in_minutes) - tf_in_minutes * 60
    return from_utc_timestamp_to_utc_dtm(recent_ot_tim)


# Returns most recent open time for given time frames as dict
def get_recent_ot_dict(time_frames):
    res = dict()

    for tf in time_frames:
        recent_ot_tim = floor_epoch_n_minutes(int(time.time()), tf.value[0]) - tf.value[0] * 60
        recent_ot = from_utc_timestamp_to_utc_dtm(recent_ot_tim)

        res[tf.value[1]] = recent_ot

    return res


# Construct empty message
def get_empty_msg_dict(time_frames):
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
