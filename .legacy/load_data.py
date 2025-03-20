import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
import time

def time_to_seconds(time_str):
    time_dict = {'1m': 60, '5m': 300, '15m': 900, '30m': 1800, 
                 '60m': 3600, '4h': 14400, '1d': 86400, '1W': 604800}
    return time_dict[time_str]

def time_to_cycles(time_str):
    time_dict = {'1m': 1440, '5m': 288, '15m': 96, '30m': 48, 
                 '60m': 24, '4h': 6, '1d': 1, '1w': 1}
    return time_dict[time_str]

base_url = 'https://www.mexc.com'
kline_endpoint = '/open/api/v2/market/kline'


def fetch_candles(symbol, interval, timeframe):
    listt = []

    now = datetime.now()
    current_time = int(now.timestamp())
    loadtime = timeframe * 24 * 60 * 60 # days * hours * minutes * seconds
    start_time = current_time - loadtime

    while True:
        
        params = {
            'symbol': symbol,
             'interval': interval,
             'limit': 500,
             'start_time': start_time
        }

        url = base_url + kline_endpoint

        while True:
            try:
                response = requests.get(url, params=params)
                if response.json()['code'] == 200:
                    break
                else:
                    print(f"Error: {response.json()['msg']}")
                    time.sleep(1)
            except Exception as e:
                print('Случилось ', e)
            
        dataa = response.json()
        br = False
        if dataa['code'] == 200:
            if dataa['data'] == []:
                br = True

            candlestick_data = dataa['data']

            data = pd.DataFrame(candlestick_data,
                                columns=['timestamp', 'open', 'close', 'high', 'low', 'volume', 'ignore'])
        
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')
        
            data.set_index('timestamp', inplace=True)
    
        else:
            print(f"Error: {dataa['msg']}")
    
        start_time += 500 * time_to_seconds(interval)
        listt.append(data)
        # print('.', end='')
        if br:
            break


    data = pd.concat(listt)
    data.pop('ignore')
    return data

if __name__ == '__main__':
    symbol = 'KAS_USDT'
    interval = '15m'
    timeframe = 350 # 30 is max for 1m | 350 is max for any other
    data = fetch_candles(symbol, interval, timeframe) # 100800 == 350
    print(data)
    data.to_pickle(f'Data/{symbol}_{interval}_{timeframe}_days_data.pkl')