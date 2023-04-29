import sqlite3
import pandas as pd
import bt

#stock_data.db에 접속
conn = sqlite3.connect('stock_data.db')
cursor = conn.cursor()

#종목코드를 입력받아서 해당 종목의 데이터를 불러옴
ticker = '005930'

#종목코드를 입력받아서 해당 종목의 데이터를 불러옴
cursor.execute("SELECT * FROM stock_data WHERE ticker = ?", (ticker,))
rows = cursor.fetchall()

#row를 dataframe으로 변환
df = pd.DataFrame(rows, columns=['코드','이름','날짜', '시가', '고가', '저가', '종가', '거래량', '거래대금', '등락률', 'BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS', '기관합계', '기타법인', '개인', '외국인합계', '전체', '시가총액', '거래량2', '거래대금2', '상장주식수', '상장주식수2', '보유수량', '지분율', '한도수량', '한도소진률'])

print(df)

