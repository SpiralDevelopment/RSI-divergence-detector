import requests as rq


class TelegramPoster:
    _token = "TG_TOKEN"
    _url = "https://api.telegram.org/bot"
    _channel_id = "TG_CHANNEL_ID"

    def __init__(self):
        self._url += self._token

    def post_msg(self, text):
        print(text)

        method = self._url + "/sendMessage?chat_id=" + self._channel_id + "&text=" + text + "&parse_mode=html"
        r = rq.post(method)

        return r.status_code
