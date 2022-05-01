import websocket,json,pprint,talib,numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET="wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
RSI_PERIOD=14
RSI_OVERBOUGHT=70
RSI_OVERSOLD=30  
TRADE_SYMBOL='ETHUSD'
TRADE_QUANTITY=0.05 

closes=[]
in_position=False
 
client =Client(config.API_KEY,config.API_SECRET,tld='us')

def order(side,symbol,quantity,order_type=ORDER_MARKET_TYPE):
    try:
        print("sending ")
        order = client.create_order(symbol=symbol, 
        side=side,
        type=order_type,
        quantity=quantity)
        print(order)
        return True

    except Exception as e:
        return False





def on_open(ws):
    print("opened connection")

def on_close(ws):
    print("closed connection")

def on_message(ws,message):
    print("received message")
    json_message=json.loads(message)
    candle=json_message['k']
    is_candle_closed=candle['x']
    close=candle['c'] 
    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close) )  
        print("closes")
        print(closes) 
        
        if len(closes)>RSI_PERIOD:
            np_closes=numpy.array(closes)
            rsi=talib.RSI(np_closes,RSI_PERIOD)
            print("all rsi's calculated so far: ")
            print(rsi)
            last_rsi=rsi[-1]
            print("the current rsi is: ")
            print(last_rsi)

            if last_rsi>RSI_OVERBOUGHT:
                if in_position:
                    print("SELL SELL SELL")
                    #binance order sell logic goes here
                    order_succeeded=order(SIDE_SELL,TRADE_SYMBOL,TRADE_QUANTITY,order_type=ORDER_MARKET_TYPE)
                    if order_succeeded:
                        in_position=False
                else:
                    print("it is overbought,but we dont own any,nothing to do")

            if last_rsi<RSI_OVERSOLD:
                if in_position:
                    print("it is oversold but i already own it and nothing to do")
                else:
                    print("BUY BUY BUY")
                    #binance order buy logic goes here
                    order_succeeded=order(SIDE_BUY,TRADE_SYMBOL,TRADE_QUANTITY,order_type=ORDER_MARKET_TYPE)
                    in_position=True

                    

                





ws=websocket.WebSocketApp(SOCKET,on_open=on_open,on_close=on_close,on_message=on_message)

ws.run_forever()