# tests/test_mexc_module.py

import pytest
from unittest.mock import patch
import pandas as pd
from LoadData import time_to_seconds, time_to_cycles, fetch_candles

# Test data for time_to_seconds
@pytest.mark.parametrize("input_str,expected", [
    ('1m', 60),
    ('5m', 300),
    ('15m', 900),
    ('30m', 1800),
    ('60m', 3600),
    ('4h', 14400),
    ('1d', 86400),
    ('1w', 604800),
])
def test_time_to_seconds(input_str, expected):
    assert time_to_seconds(input_str) == expected

# Test data for time_to_cycles
@pytest.mark.parametrize("input_str,expected", [
    ('1m', 1440),
    ('5m', 288),
    ('15m', 96),
    ('30m', 48),
    ('60m', 24),
    ('4h', 6),
    ('1d', 1),
    ('1w', 1),
])
def test_time_to_cycles(input_str, expected):
    assert time_to_cycles(input_str) == expected

# Mock response for fetch_candles
@pytest.fixture
def mock_requests_get_success():
    with patch('mexc_module.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            'code': 200,
            'data': [
                [1609459200, '0.1', '0.2', '0.3', '0.0', '1000', 'ignore']
            ]
        }
        yield mock_get

@pytest.fixture
def mock_requests_get_failure():
    with patch('mexc_module.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.json.return_value = {
            'code': 400,
            'msg': 'Bad Request'
        }
        yield mock_get

def test_fetch_candles_success(mock_requests_get_success):
    symbol = 'TEST_USDT'
    interval = '1m'
    timeframe = 1  # 1 day

    df = fetch_candles(symbol, interval, timeframe)
    
    # Verify the DataFrame structure
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    expected_columns = ['open', 'close', 'high', 'low', 'volume']
    assert list(df.columns) == expected_columns
    
    # Verify data types
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.api.types.is_float_dtype(df['open'])
    assert pd.api.types.is_float_dtype(df['close'])
    assert pd.api.types.is_float_dtype(df['high'])
    assert pd.api.types.is_float_dtype(df['low'])
    assert pd.api.types.is_float_dtype(df['volume'])

def test_fetch_candles_api_failure(mock_requests_get_failure, capsys):
    symbol = 'TEST_USDT'
    interval = '1m'
    timeframe = 1  # 1 day

    df = fetch_candles(symbol, interval, timeframe)
    
    # Expecting empty DataFrame due to API failure
    assert df.empty
    
    # Capture printed output
    captured = capsys.readouterr()
    assert 'Error: Bad Request' in captured.out
