#!/usr/bin/env python3

import os, sys
import time
import contextlib
from json import dumps

from requests.exceptions import ReadTimeout as RequestsReadTimeout

from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance import enums, helpers

msg = print


#msg('os.environ:', dumps(dict(os.environ)))
api_key, api_secret = map(os.environ.get, 'BINANCE_API_KEY  BINANCE_API_SECRET'.split())

#api_key = os.environ['
#api_secret = os.environ['
msg('api_key:', api_key)
msg('api_secret:', api_secret)
#sys.exit()



# ordered list of intervals and their Binance token

KLINE_INTERVALS = (
    enums.KLINE_INTERVAL_1MINUTE,
    enums.KLINE_INTERVAL_3MINUTE,
    enums.KLINE_INTERVAL_5MINUTE,
    enums.KLINE_INTERVAL_15MINUTE,
    enums.KLINE_INTERVAL_30MINUTE,
    enums.KLINE_INTERVAL_1HOUR,
    enums.KLINE_INTERVAL_2HOUR,
    enums.KLINE_INTERVAL_4HOUR,
    enums.KLINE_INTERVAL_6HOUR,
    enums.KLINE_INTERVAL_8HOUR,
    enums.KLINE_INTERVAL_12HOUR,
    enums.KLINE_INTERVAL_1DAY,
    enums.KLINE_INTERVAL_3DAY,
    enums.KLINE_INTERVAL_1WEEK,
#    enums.KLINE_INTERVAL_1MONTH,
)

kline_intervals = tuple((helpers.interval_to_milliseconds(token), token) for token in KLINE_INTERVALS)
#msg('kline_intervals:', dumps(kline_intervals))
#sys.exit()

# Take a sequence of dicts and return a dict of the dicts, where the
# key in the outer dict is the value at that key in each inner dict
def normalize(key, seq): return dict((item[key], item) for item in seq)


client = Client(api_key, api_secret, {'timeout': 10})


class throttler(object):
    def __init__(self, interval):
        self.interval = interval
        self.wait_until = time.monotonic()

    def __enter__(self):
        delay = self.wait_until - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        return self.wait_until, delay

    def __exit__(self, *exc):
        self.wait_until = time.monotonic() + self.interval
        return False

def make_throttle(interval):

    next_time = [time.monotonic()]
    @contextlib.contextmanager
    def throttle():
        wait_until = next_time[0]
        delay = wait_until - time.monotonic()
        if delay > 0:
            time.sleep(delay)



# seconds between calls at 8 per second
THROTTLE_INTERVAL = 1 / 8 # Python 3
# seconds between calls at 32 calls per 3 seconds (just under 10 / sec)
THROTTLE_INTERVAL = 3 / 32 # Python 3
#next_time = [time.monotonic()]

throttle = throttler(THROTTLE_INTERVAL)


msg()
with throttle: pass
msg('ping:', dumps(client.ping()))
msg()

timings = list()
def get_it(item_name, msg=None, **kwargs):
    attr = 'get_' + item_name
    getter = getattr(client, attr)
    msg and msg('get_it():', dumps(dict(attr=attr, kwargs=kwargs)))

    with throttle as (wait_until, delay): pass
    if False:
        wait_until = next_time[0]
        delay = wait_until - time.monotonic()
        if delay > 0:
            time.sleep(delay)

    call_start_time = time.monotonic()
    try:
        item = getter(**kwargs)
    except (BinanceAPIException, RequestsReadTimeout) as exc:
        print('Exception in get_it():', str(type(exc)), dumps(dict(call=attr, kwargs=kwargs, exc=str(exc))))
        item = None
    call_end_time = time.monotonic()

    #next_time[0] = call_start_time + THROTTLE_INC

    timing = dict(call=attr, call_start_time=call_start_time, delay=delay, delta=call_start_time-wait_until, calltime=call_end_time-call_start_time)
    timings.append(timing)

    msg and msg(item_name +':', dumps(item))
    return item


#get_it('server_time')
timing_sync = get_it('server_time')
timing_sync['hostTime'] = int(1000*time.time())
msg('timing_sync:', dumps(timing_sync))

if False:
    timing_sync2 = get_it('server_time')
    timing_sync2['hostTime'] = int(1000*time.time())
    msg('timing_sync2:', dumps(timing_sync2))

    timing_sync3 = get_it('server_time')
    timing_sync3['hostTime'] = int(1000*time.time())
    msg('timing_sync3:', dumps(timing_sync3))

    msg('timings:', dumps(timings))
    #sys.exit()

if False:
    time_res = client.get_server_time()
    msg('time_res:', dumps(time_res))
    msg()

    exchange_info = client.get_exchange_info()
    msg('exchange_info:', dumps(exchange_info))
    msg()

    BNBETH_info = client.get_symbol_info('BNBETH')
    msg('BNBETH_info:', dumps(BNBETH_info))
    msg()

    all_tickers = client.get_all_tickers()
    msg('all_tickers:', dumps(all_tickers))
    msg()


    ETH_balance = client.get_asset_balance('ETH')
    msg('ETH_balance:', ETH_balance)
    msg()

    account = client.get_account()
    msg('account:', dumps(account))
    msg()

    deposit_history = client.get_deposit_history()
    msg('deposit_history:', dumps(deposit_history))
    msg()

    get_it('my_trades', symbol='XVGETH')

#get_it('symbol_ticker', symbol='XVGETH')
#get_it('symbol_ticker', symbol='XVGETH LSKETH'.split())
#get_it('symbol_ticker', symbols='XVGETH LSKETH')

BOGUS_SYMBOLS = '123 456'.split()
TRADE_QUOTE_ASSETS = 'BTC ETH'.split()
TRADE_QUOTE_ASSETS = 'ETH'.split()

def get_exchange():
    exchange_info = get_it('exchange_info', False)
    symbols_full = exchange_info['symbols']

    if True:
        quote_assets = tuple(sorted(set(symbol['quoteAsset'] for symbol in symbols_full if symbol['quoteAsset'] not in BOGUS_SYMBOLS)))
        trade_quote_assets = tuple(sorted(set(TRADE_QUOTE_ASSETS)))
        base_assets = tuple(sorted(set(symbol['baseAsset'] for symbol in symbols_full if symbol['quoteAsset'] not in BOGUS_SYMBOLS)))
        symbols = tuple(sorted(set(symbol['symbol'] for symbol in symbols_full)))
    else:
        assert False
        quote_assets = set(symbol['quoteAsset'] for symbol in symbols_full)
        base_assets = set(symbol['baseAsset'] for symbol in symbols_full)
        symbols = set(symbol['symbol'] for symbol in symbols_full)

    return dict(quoteAssets=quote_assets, tradeQuoteAssets=trade_quote_assets, baseAssets=base_assets, symbols=symbols, zz_exchange_info=exchange_info)
#msg('get_exchange():', dumps(get_exchange()))
#sys.exit()

exchange = get_exchange()

# symbol='ADAETH' -> baseAsset='ADA', quoteAsset='ETH'
assets_by_symbol = dict(('{}{}'.format(base_asset, quote_asset), dict(baseAsset=base_asset, quoteAsset=quote_asset))
                        for  base_asset in exchange['baseAssets']
                        for  quote_asset in exchange['tradeQuoteAssets'])
# ensures uniqueness of symbol joins -- really wish they'd used a separator
assert len(assets_by_symbol) == len(exchange['baseAssets']) * len(exchange['tradeQuoteAssets']), str((len(assets_by_symbol), len(exchange['baseAssets']), len(exchange['tradeQuoteAssets'])))


# Deal with quantities as strings: e.g.:  "free": "0.03725243",  "free": "0.00000000"
#zero = set('0.')

account = get_it('account')
msg('account:', dumps(account))
#account_assets = tuple(asset for asset in account['balances'] if set(asset['free']) != zero)
account_assets = normalize('asset', (asset for asset in account['balances'] if float(asset['free']) > 0))
msg('account_assets:', dumps(account_assets))
#sys.exit()


# string quantity values to scaled ints, and back
DECIMALS = 8
def quantity_to_int(quantity):
    assert type(quantity) is str, str((quantity, type(quantity)))
    whole, fraction = quantity.split('.')
    assert whole and fraction, str((quantity, whole, fraction))

    # build a string that will parse to int

    # pad with trailing zeros
    while len(fraction) < DECIMALS:
        fraction += '0'
    # limit to length DECIMALS
    fraction = fraction[:DECIMALS]

    # join the strings
    text = whole + fraction
    # strip off leading zeros (because of int literal semantics of Python: https://docs.python.org/3/reference/lexical_analysis.html#integer-literals)
    while text and text.startswith('0'):
        text = text[1:]
    # "special" case
    if not text:
        text = '0'

    return int(text)

def int_to_quantity(value):
    assert type(value) is int, str((value, type(value)))
    text = str(value)
    while len(text) <= DECIMALS:
        text = '0' + text
    whole, fraction = text[:-DECIMALS], text[-DECIMALS:]
    while len(fraction) < DECIMALS:
        fraction += '0'
    return '.'.join((whole, fraction))


ass = normalize('asset', (asset for asset in account['balances']))
ass2 = dict((asset, dict(free=item['free'], quantity_int=quantity_to_int(item['free']), quantity_str=int_to_quantity(quantity_to_int(item['free']))))
                       for asset, item in ass.items())
msg('ass2:', dumps(ass2))
assert all(item['quantity_str'] == item['free'] for item in ass2.values())

msg('quantities:', dumps(dict((asset, dict(quantity_str=item['free'], quantity_int=quantity_to_int(item['free'])))
                              for asset, item in account_assets.items())))


def get_trade_times():

    #possible_trade_symbols = tuple('{}{}'.format(asset['asset'], quote_asset) for asset in account_assets for quote_asset in exchange['quoteAssets'])
    possible_trade_symbols = tuple('{}{}'.format(asset['asset'], quote_asset)
                                   for asset in account_assets.values()
                                   for quote_asset in exchange['tradeQuoteAssets'])

    possible_trade_symbols = set(possible_trade_symbols) & set(exchange['symbols'])
    msg('possible_trade_symbols:', dumps(sorted(possible_trade_symbols)))

    trades = tuple(dict(symbol=possible_trade_symbol, trades=get_it('my_trades', msg=False, symbol=possible_trade_symbol, limit=5)) for possible_trade_symbol in possible_trade_symbols)
    trades = tuple(trade for trade in trades if trade['trades'])

    return trades

#    return possible_trade_symbols
#    return exchange


trade_times = get_trade_times()
msg('trade_times:', dumps(trade_times))
trade_times2 = normalize('symbol', trade_times)
msg('trade_times2:', dumps(trade_times2))
#sys.exit()



# Kline data
"""
From: https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_historical_trades
From: https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#klinecandlestick-data
        1499040000000,      # Open time
        "0.01634790",       # Open
        "0.80000000",       # High
        "0.01575800",       # Low
        "0.01577100",       # Close
        "148976.11427815",  # Volume
        1499644799999,      # Close time
        "2434.19055334",    # Quote asset volume
        308,                # Number of trades
        "1756.87402397",    # Taker buy base asset volume
        "28.46694368",      # Taker buy quote asset volume
        "17928899.62484339" # Can be ignored
"""

KLINER_FIELDS = 'openTime open high low close volume closeTime'.split()
def kliner(interval, start_time):
    def do_kliner(values):
        klines = dict(interval=interval, startTimeHsw=start_time)
        klines.update(zip(KLINER_FIELDS, values))
        return klines
    return do_kliner

def get_symbol_klines(symbol, start_time):
    # get at least 100 measures (so we can discard 3% as outliers)
    interval_msec = timing_sync['serverTime'] - start_time
    #msg('get_symbol_klines():', symbol, 'interval_msec', interval_msec)
    delta = interval_msec // 100
    assert delta > 0, str((interval_msec, delta))

    for msec, token in reversed(kline_intervals):
        if msec <= delta: break
    assert 0 < msec <= delta and token, str((interval_msec, delta, msec, token))

    all_klines = list()
#    for interval in (enums.KLINE_INTERVAL_1MONTH, enums.KLINE_INTERVAL_1DAY, enums.KLINE_INTERVAL_1HOUR, enums.KLINE_INTERVAL_1MINUTE):
    for interval in (token,):
        klines = get_it('klines', symbol=symbol, startTime=start_time, interval=interval)
        #print('get_symbol_klines:', symbol, interval, start_time, len(klines))
        if klines:
            all_klines.extend(map(kliner(interval, start_time), klines))
            start_time = all_klines[-1]['openTime']
            #start_time = all_klines[-1]['closeTime']
    return all_klines

def get_klines():
    klines = tuple(dict(symbol=trade['symbol'], klines=get_symbol_klines(symbol=trade['symbol'], start_time=trade['trades'][0]['time']))
                   for trade in trade_times)
#                   for trade in trade_times if trade['symbol'] == 'BTGBTC')
    return klines

klines = get_klines()
msg('klines:', dumps(klines))



all_tickers = get_it('all_tickers')
current_time = get_it('server_time')['serverTime']
#msg('all_tickers:', dumps(all_tickers))
#all_tickers2 = dict((ticker['symbol'], ticker) for ticker in all_tickers)
all_tickers2 = normalize('symbol', all_tickers)
msg('all_tickers2:', dumps(all_tickers2))

def find_lows(klines):
    res = list()
    for symbol_klines in klines:
        symbol = symbol_klines['symbol']
        base_asset = assets_by_symbol[symbol]['baseAsset']
        quote_asset = assets_by_symbol[symbol]['quoteAsset']

        free_quantity = account_assets[base_asset]['free']
        #free_quantity = tuple(account_assets[baseAsset].split('.'))

        lows = sorted(kline['low'] for kline in symbol_klines['klines'])
        assert len(lows) >= 100, str((symbol, len(lows)))
        most_recent_trade = trade_times2[symbol]['trades'][0]
        trade_price = most_recent_trade['price']
        trade_time = most_recent_trade['time']
        # lowest, lower = 3rd percentile, low = 5th percentile
        low, lower, lowest = (lows[pct * len(lows) // 100] for pct in (5, 3, 0))
        current_price = all_tickers2[symbol]['price']

        price_fraction = float(current_price)/min(float(low), float(trade_price))

        res.append(dict(symbol=symbol,
                        base_asset=base_asset,
                        quote_asset=quote_asset,
                        free_quantity=free_quantity,
                        trade_price=trade_price,
                        trade_time=trade_time,
                        low=low,
                        lower=lower,
                        lowest=lowest,
                        current_price=current_price,
                        current_time=current_time,
                        price_fraction=price_fraction))
    return normalize('symbol', res)

lows = find_lows(klines)
msg('lows:', dumps(lows))

price_threshold = 1.25
trade_em = dict((symbol, item) for symbol, item in lows.items() if item['price_fraction'] >= price_threshold)

trade_fraction = 3 / 32
for item in trade_em.values():
    #item['trade_quantity'] = float(item['free_quantity']) * trade_fraction
    #item['sell_quantity'] = int_to_quantity(quantity_to_int(item['free_quantity']) * 3 // 32)
    item['sell_quantity'] = int_to_quantity(quantity_to_int(item['free_quantity']) // 10)

msg('trade_em:', dumps(trade_em))

#klines2 = get_klines(enums.KLINE_INTERVAL_1DAY)
#msg('klines2:', dumps(klines2))

msg('timings:', dumps(timings))
