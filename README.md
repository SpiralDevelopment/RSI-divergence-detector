# RSI-divergence-detector
> Relative Strength Index Divergence Detector

**RSI divergence detector finds regular/hidden bullish and bearish divergences for given data**

The underlying algorithm of this project has been used to detect RSI divergences for some top coins on Binance and post the results here on [Twitter](https://twitter.com/rsindicator) and here on [Telegram](https://t.me/relative_strength_index)

## Usage

This project uses [TaLib](https://github.com/mrjbq7/ta-lib) library for some calculations, so [install](https://github.com/mrjbq7/ta-lib#installation) the TaLib library first.
Then clone the project and install other requirements.

```bash
$ git clone git@github.com:SpiralDevelopment/crypto-hft-data.git
$ cd crypto-hft-data
$ pip3 install virtualenv
$ virtualenv env
$ source env/bin/activate
$ pip3 install -r requirements.txt
```

### Samples

There are 2 samples available
- sample_tg_poster.py - Gets the ohlc data from local database and checks if the last closed candle has any form of RSI divergence. 
  The result of this script is posted to Telegram channel [here](https://t.me/relative_strength_index)
- sample_binance.py - Gets the data from Binance API and plots ALL detected RSI divergences during that period

## How it looks

Here is the result of detected RSI divergences for BTCUSDT symbol during 22.11.2020-22.03.2022 period. 

- Red lines - Regular and hidden Bearish divergences 
- Blue lines - Regular and hidden Bullish divergences

<p align="center"><img src="./btcusdt_divergences.PNG"></p>


## License
[MIT License](https://github.com/SpiralDevelopment/RSI-divergence-detector/blob/main/LICENSE)
