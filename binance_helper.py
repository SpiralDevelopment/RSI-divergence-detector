import json
import requests


class BinanceHelper(object):
    ALL_PAIRS = None

    def __init__(self):
        pass

    @staticmethod
    def get_all_market_pairs():
        try:
            if BinanceHelper.ALL_PAIRS:
                return BinanceHelper.ALL_PAIRS
            else:
                response = requests.get("https://api.binance.com/api/v1/exchangeInfo")
                res_json = json.loads(response.text)

                symbols = res_json.get('symbols', None)
                markets = []

                for item in symbols:
                    if item['status'] == "TRADING":
                        markets.append(item['symbol'])

                BinanceHelper.ALL_PAIRS = markets

                return markets
        except requests.exceptions.RequestException as e:
            return None
