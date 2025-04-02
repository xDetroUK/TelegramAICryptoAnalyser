import openai

class ChatAnalysis:
    def __init__(self, api_key):
        self.client = openai.Client(api_key=api_key)
    def simpleAnalyze(self,data,orderbook,curprice,value='BTCUSDT'):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"you'll receive information about {value}:open_time,open,high,low,close,volume values in\
                    1 minute candle interval, orderbook information about the 25 largest orders and current price.\
                  Analyze all of the data and recognize candle stick patterns and all other methods necessary to \
                 predict the price in the next 30-45 minutes with at least 92% accuracy! I want from you to give me \
                 exact order to execute with an entry point , stop loss and take profit\
                  .Keep the reply short and simple with exact numbers and orders that are at least 92% accurate!"},
                {"role": "user",
                 "content": f"open_time,open,high,low,close,volume:{data}\n"
                            f"Orderbook: {orderbook}\n"
                            f"Current Price: {curprice}"},
            ]
        )
        return response.choices[0].message.content

    def LongTermAnalyze(self,data,orderbook,curprice,value='BTCUSDT'):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"First you'll receive information about {value}: open_time,open,high,low,close and volume \
                 in 1 hour candle interval, order book information about the 25 largest orders and current price  \
                 .Analyze all of the data and use candle stick patterns and all other methods necessary to\
                   predict the price in the next 1 hour give me only exact order to execute with\
                    exact entry, stop loss and take profit that are at least 92% accurate! \
                   Stick to short simple and clear answers only with exact numbers and short suggestion!"},
                {"role": "user",
                 "content": f"open_time,open,high,low,close,volume:{data}\n"
                            f"Orderbook: {orderbook}\n"
                            f"Current Price: {curprice}"},
            ]
        )
        return response.choices[0].message.content

    def customAnalyze(self,data,orderbook,curprice,value='BTCUSDT',cuscommand=""):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": f"you'll receive information about {value} open_time,open,high,low,close and volume values for the last 500 candles \n"
                            f"Orderbook information about the largest 25 orders and current price.{cuscommand}\n"
                            f" stick to short and simple answears only with exact numbers for entry,take profit, stop loss that are for sure 90% accurate!"},
                {"role": "user",
                 "content": f"open_time,open,high,low,close,volume:{data}\n"
                            f"Orderbook: {orderbook}\n"
                            f"Current Price: {curprice}"},
            ])
        return response.choices[0].message.content

