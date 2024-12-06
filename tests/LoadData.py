import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
start_time = time.time()


def time_to_seconds(time_str):
    time_dict = {'1m': 60, '5m': 300, '15m': 900, '30m': 1800, 
                 '60m': 3600, '4h': 14400, '1d': 86400, '1w': 604800}
    return time_dict[time_str]

def time_to_cycles(time_str):
    time_dict = {'1m': 1440, '5m': 288, '15m': 96, '30m': 48, 
                 '60m': 24, '4h': 6, '1d': 1, '1w': 1}
    return time_dict[time_str]

# Define MEXC API endpoints
base_url = 'https://www.mexc.com'
kline_endpoint = '/open/api/v2/market/kline'

def fetch_candles(symbol, interval, timeframe):
    listt = []

    now = datetime.now()
    current_time = int(now.timestamp())
    loadtime = timeframe * 24 * 60 * 60 # days * hours * minutes * seconds
    start_time = current_time - loadtime

    for i in range(time_to_cycles(interval)):
        
        params = {
            'symbol': symbol,
             'interval': interval,
             #'limit': 999, default == 500
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
        
        if dataa['code'] == 200:
            if dataa['data'] == []:
                break

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


    data = pd.concat(listt)
    data.pop('ignore')
    return data


if __name__ == '__main__':
    symbol = 'KAS_USDT'
    interval = '1m'
    timeframe = 10 # timeframe < 600!!!, counted in days

    data = fetch_candles(symbol, interval, timeframe) # берем данные
    print(data)
    data.to_pickle(f'Data/{symbol}_{interval}_{timeframe}_days_data.pkl')




    print()
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Time taken: ", str(timedelta(seconds=elapsed_time)), "часы:минуты:секунды") 
    print(' ')
    print("---------------------------------------------------------------------------------------------------------------")
    print(' ')

