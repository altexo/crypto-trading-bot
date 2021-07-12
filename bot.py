import websocket # From lib websocket_client
import talib
import config
import pprint
import json 
import numpy
from binance.client import Client
from binance.enums import *

# Binance  socket
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.05

# Candle closes array
closes = []
# Bool to check if there´s a position already open
in_position = False

# Binance client
client = Client(config.API_KEY, config.API_SECRET, tld='us')

def order(side, quantity, symbol, order_type = ORDER_TYPE_MARKET):
    try:
        print("sending order")
        return True
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity )
        print(order)
    except Exception as e:
        return False

    return True

def on_open(ws):
    print('Opened connection')

def on_close(ws):
    print('Closed connection')

def on_message(ws, message):
    global closes
    print('===================================')
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        
        print('Candle closed at {} '. format(close))
        closes.append(float(close))
        print('Closes')
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("All rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("The current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell! Sell! ")
                     # write binance sell logic
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                         in_position = False
                else:
                    print("Is overbought but, we don't own any position to sell, nothing to do.")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but  you already own a position, nothing to do.")
                else:
                    print("Buy! Buy!")
                    # write binance order logic
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                         in_position = False

# Init socket
ws = websocket.WebSocketApp( SOCKET, on_open=on_open, on_close=on_close, on_message=on_message )

ws.run_forever()