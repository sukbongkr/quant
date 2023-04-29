from pykrx import stock
import datetime
import pandas as pd
from tqdm import tqdm
import sqlite3

# 1. 전체 종목 코드 조회
tickers = stock.get_market_ticker_list(market="ALL")

end_date = datetime.datetime.now().strftime("%Y%m%d")

# Create a SQLite connection and create the table if not exists
conn = sqlite3.connect('stock_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS stock_data
                 (ticker TEXT,이름 TEXT, 날짜 TEXT, 시가 REAL, 고가 REAL, 저가 REAL, 종가 REAL, 거래량 REAL, 거래대금 REAL, 등락률 REAL, BPS REAL, PER REAL, PBR REAL, EPS REAL, DIV REAL, DPS REAL, 기관합계 REAL, 기타법인 REAL, 개인 REAL, 외국인합계 REAL, 전체 REAL, 시가총액 REAL, 거래량2 REAL, 거래대금2 REAL, 상장주식수 REAL, 상장주식수2 REAL, 보유수량 REAL, 지분율 REAL, 한도수량 REAL, 한도소진률 REAL)''')

# start_date 는 db에 저장된 마지막 날짜에서 다음날로 설정
start_date = cursor.execute("SELECT 날짜 FROM stock_data ORDER BY 날짜 DESC LIMIT 1").fetchone()

print(start_date)

# 만일 db에 날짜정보가 없다면 1956년 3월 3일로 설정
if start_date is None:
    start_date = "19560303"

error_list = {}

bar = tqdm(tickers)

for ticker in bar:
    try:
        price = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
        value = stock.get_market_fundamental(start_date, end_date, ticker)
        trading = stock.get_market_trading_value_by_date(start_date, end_date, ticker)
        totalprice = stock.get_market_cap(start_date, end_date, ticker)
        foreign = stock.get_exhaustion_rates_of_foreign_investment(start_date, end_date, ticker)

        #value가 비어있을 경우 빈 데이터프레임 생성
        if value.empty:
            value = pd.DataFrame(columns=['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS'])
 
        # 데이터 프레임을 결합하고 열 이름을 변경합니다.
        df = pd.concat([price, value, trading, totalprice, foreign], axis=1)
        
        df.reset_index(inplace=True)
        df.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량', '거래대금', '등락률', 'BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS', '기관합계', '기타법인', '개인', '외국인합계', '전체', '시가총액', '거래량2', '거래대금2', '상장주식수', '상장주식수2', '보유수량', '지분율', '한도수량', '한도소진률']

        # ticker 정보를 추가하고 데이터베이스에 저장합니다.
        df['ticker'] = ticker
        df['이름'] = stock.get_market_ticker_name(ticker)
        df.to_sql("stock_data", conn, if_exists="append", index=False)
    
    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")
        #에러리스트에 추가해서 저장
        error_list[ticker] = e

print(error_list)

conn.commit()
conn.close()
bar.close()