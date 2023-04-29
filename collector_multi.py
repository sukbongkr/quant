import concurrent.futures
from pykrx import stock
import datetime
import pandas as pd
from tqdm import tqdm
import sqlite3

def process_ticker(ticker, start_date, end_date):
    try:
        price = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
        value = stock.get_market_fundamental(start_date, end_date, ticker)
        trading = stock.get_market_trading_value_by_date(start_date, end_date, ticker)
        totalprice = stock.get_market_cap(start_date, end_date, ticker)
        foreign = stock.get_exhaustion_rates_of_foreign_investment(start_date, end_date, ticker)

        if value.empty:
            value = pd.DataFrame(columns=['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS'])

        df = pd.concat([price, value, trading, totalprice, foreign], axis=1)

        df.reset_index(inplace=True)
        df.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량', '거래대금', '등락률', 'BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS', '기관합계', '기타법인', '개인', '외국인합계', '전체', '시가총액', '거래량2', '거래대금2', '상장주식수', '상장주식수2', '보유수량', '지분율', '한도수량', '한도소진률']

        df['ticker'] = ticker
        df['이름'] = stock.get_market_ticker_name(ticker)

        return df

    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
        return None

tickers = stock.get_market_ticker_list(market="ALL")
end_date = datetime.datetime.now().strftime("%Y%m%d")

conn = sqlite3.connect('stock_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS stock_data
                 (ticker TEXT, 이름 TEXT, 날짜 TEXT, 시가 REAL, 고가 REAL, 저가 REAL, 종가 REAL, 거래량 REAL, 거래대금 REAL, 등락률 REAL, BPS REAL, PER REAL, PBR REAL, EPS REAL, DIV REAL, DPS REAL, 기관합계 REAL, 기타법인 REAL, 개인 REAL, 외국인합계 REAL, 전체 REAL, 시가총액 REAL, 거래량2 REAL, 거래대금2 REAL, 상장주식수 REAL, 상장주식수2 REAL, 보유수량 REAL, 지분율 REAL, 한도수량 REAL, 한도소진률 REAL)''')

start_date = cursor.execute("SELECT 날짜 FROM stock_data ORDER BY 날짜 DESC LIMIT 1").fetchone()

if start_date is None:
    start_date = "19560303"

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(tqdm(executor.map(process_ticker, tickers, [start_date] * len(tickers), [end_date] * len(tickers)), total=len(tickers)))

for df in results:
    if df is not None:
        df.to_sql("stock_data", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("작업 완료!")
