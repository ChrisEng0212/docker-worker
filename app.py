import os, json, math
from celery import Celery
from celery.utils.log import get_task_logger
from celery.contrib.abortable import AbortableTask
from time import sleep
from pybit import inverse_perpetual, usdt_perpetual
import datetime as dt
from datetime import datetime
import redis
import time
import pickle

from math import trunc


session = inverse_perpetual.HTTP(
    endpoint='https://api.bybit.com'
)


r = redis.Redis(
    host='redis',
    port=6379,
    password='password',
    decode_responses=True
    )

print('REDIS', r)



GREETING = os.getenv('GREETING')

print(GREETING)




def compiler(message, pair, coin):

    if r.get('buy'):
        print(json.loads(r.get('buy')))

    timestamp = message[0]['timestamp']
    ts = str(datetime.strptime(timestamp.split('.')[0], "%Y-%m-%dT%H:%M:%S"))
    trade_time_ms = int(message[0]['trade_time_ms'])


    sess = session.latest_information_for_symbol(symbol=pair)
    streamOI = sess['result'][0]['open_interest']
    streamTime = round(float(sess['time_now']), 1)
    # print(streamTime)
    streamPrice = float(sess['result'][0]['last_price'])



    buyUnit = {
                    'side' : 'Buy',
                    'size' : 0,
                    'trade_time_ms' : trade_time_ms,
                    'timestamp' : ts,
                    'streamTime' : streamTime,
                    'streamPrice' : streamPrice,
                    'streamOI' : streamOI,
                    'tradecount' : 0,
                    'spread' : {}
                }

    sellUnit = {
                    'side' : 'Sell',
                    'size' : 0,
                    'trade_time_ms' : trade_time_ms,
                    'timestamp' : ts,
                    'streamTime' : streamTime,
                    'streamPrice' : streamPrice,
                    'streamOI' : streamOI,
                    'tradecount' : 0,
                    'spread' : {}
    }

    for x in message:

        size = x['size']

        if coin == 'BTC':
            #  21010.51 -->  42020.2 --> 42020 --> 21010.5
            priceString = str(  round  ( float(x['price'])  *2 )/2)
        elif coin == 'ETH':
            # 1510.21 -->  30204.2 --> 30204 --> 15102 --> 1510.2
            priceString = str(  round  ( float(x['price'])  *100 )/100)
        elif coin == 'SOL':
            # 23.645  -->  23.645 --> 30204 --> 15102 --> 1510.2
            priceString = str(  round  ( float(x['price'])  *100 )/100)
            size = round ( x['size']*10  )  / 10
        elif coin == 'GALA':
            # 0.04848 -- >
            priceString = str(  round  ( float(x['price'])  *100000 )/100000)
            size = round ( x['size']*10  )  / 10
        elif coin == 'BIT':
            # 0.5774
            priceString = str(  round  ( float(x['price'])  *10000 )/10000)
            size = round ( x['size']*10  )  / 10

        if x['side'] == 'Buy':
            spread = buyUnit['spread']
            if priceString not in spread:
                spread[priceString] = size
            else:
                spread[priceString] += size

            buyUnit['size'] += size
            buyUnit['tradecount'] += 1

        if x['side'] == 'Sell':
            spread = sellUnit['spread']
            if priceString not in spread:
                spread[priceString] = size
            else:
                spread[priceString] += size

            sellUnit['size'] += x['size']
            sellUnit['tradecount'] += 1

    # print(coin + ' COMPILER RECORD:  Buys - ' + str(buyUnit['size']) + ' Sells - ' + str(sellUnit['size']) )

    r.set('buy', json.dumps(buyUnit))

    return [buyUnit, sellUnit]


def handle_trade_message(msg):

    pair = msg['topic'].split('.')[1]
    coin = pair.split('USD')[0]


    compiledMessage = compiler(msg['data'], pair, coin)


    # print('COMPILER DONE')

    buyUnit = compiledMessage[0]
    sellUnit = compiledMessage[1]

    print('Compiled B:' + str(buyUnit['size']) + ' S:' + str(sellUnit['size']))



def runStream():

    print('RUN_STREAM')    # rK = json.loads(r.keys())



    print('WEB_SOCKETS')

    ws_inverseP = inverse_perpetual.WebSocket(
        test=False,
        ping_interval=30,  # the default is 30
        ping_timeout=None,  # the default is 10 # set to None and it will never timeout?
        domain="bybit"  # the default is "bybit"
    )

    coins = ["BTCUSD"]

    ws_inverseP.trade_stream(
        handle_trade_message, coins
    )

    # ws_usdtP = usdt_perpetual.WebSocket(
    #     test=False,
    #     ping_interval=30,  # the default is 30
    #     ping_timeout=None,  # the default is 10 # set to None and it will never timeout?
    #     domain="bybit"  # the default is "bybit"
    # )

    # ws_usdtP.trade_stream(
    #     handle_trade_message, ["GALAUSDT"]
    # )


    # ws_inverseP.instrument_info_stream(
    #     handle_info_message, "BTCUSD"
    # )

    while True:
        sleep(0.1)

    return print('Task Closed')


runStream()





