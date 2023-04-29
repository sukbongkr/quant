from pykrx import stock
import datetime
import pandas as pd
from tqdm import tqdm

# 1. 전체 종목 코드 조회
tickers = stock.get_market_ticker_list(market="ALL")

start_date = "20190101"
end_date = datetime.datetime.now().strftime("%Y%m%d")

bar = tqdm(tickers)
# 2. 종목별 주가(시가, 고가, 저가, 종가, 거래량) 조회
for ticker in bar:
    price = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
    
    value = stock.get_market_fundamental(start_date,end_date,ticker)

    trading = stock.get_market_trading_value_by_date(start_date, end_date, ticker)
   
    totalprice = stock.get_market_cap(start_date, end_date, ticker)
    
    foreign = stock.get_exhaustion_rates_of_foreign_investment(start_date, end_date, ticker)

    df = pd.concat([price, value, trading, totalprice, foreign],axis=1)

    df.to_csv("./data/{}.csv".format(ticker))

bar.close()    