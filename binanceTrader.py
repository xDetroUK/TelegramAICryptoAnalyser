from binance.client import Client
import pandas as pd

class coinTrader:
    def __init__(self):
        self.api_key = ''
        self.api_secret = ''
        self.client = Client(self.api_key, self.api_secret)


    def calculate_RSI(self, df, column='close', period=4):
        delta = df[column].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        RS = gain / loss
        RSI = 100 - (100 / (1 + RS))
        return RSI

    def calculate_SMA(self, df, column='close', period=50):
        return df[column].rolling(window=period).mean()

    def calculate_EMA(self, df, column='close', period=26):
        return df[column].ewm(span=period, adjust=False).mean()

    def calculate_MACD(self, df, column='close', slow=26, fast=12):
        fast_ema = self.calculate_EMA(df, column, fast)
        slow_ema = self.calculate_EMA(df, column, slow)
        df['MACD_line'] = fast_ema - slow_ema
        df['Signal_line'] = df['MACD_line'].ewm(span=9, adjust=False).mean()
        df['MACD_histogram'] = df['MACD_line'] - df['Signal_line']
        return df

    def get_price(self,symbol):
        """Get the current price of a given symbol"""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        return float(ticker['price'])

    def fetch_historical_data(self, symbol, interval, start_date, end_date='now'):
        klines = self.client.get_historical_klines(symbol, interval, start_date, end_date if end_date != 'now' else None)
        columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                   'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        df = pd.DataFrame(klines, columns=columns)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df.set_index('open_time', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'volume']]

        orderb = []
        order_book = self.client.get_order_book(symbol=symbol, limit=5000)
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'quantity'], dtype=float)
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'quantity'], dtype=float)
        bids_df_sorted = bids_df.sort_values(by='quantity', ascending=False)
        asks_df_sorted = asks_df.sort_values(by='quantity', ascending=False)

        # Convert DataFrame to string and then append
        orderb.append("Top 25 Bids by Quantity:\n" + bids_df_sorted.head(25).to_string(index=False) + "\n")
        orderb.append("Top 25 Asks by Quantity:\n" + asks_df_sorted.head(25).to_string(index=False))

        return df,orderb


x = coinTrader()
x.fetch_historical_data("BTCUSDT","1h","1 Jan 2024")