import sqlite3
import pandas as pd

#stock_data.db에 접속
conn = sqlite3.connect('stock_data.db')
cursor = conn.cursor()

def get_stock(ticker):
    # 종목코드를 입력받아 해당 종목의 데이터를 불러옴
    # 필요한 데이터만 가져오도록 SQL 쿼리 수정
    cursor.execute("SELECT 날짜, 이름, 종가 FROM stock_data WHERE ticker = ?", (ticker,))
    rows = cursor.fetchall()

    # 결과를 바로 데이터프레임으로 변환하고, 인덱스를 설정
    df = pd.DataFrame(rows, columns=['날짜', '이름', '종가']).set_index('날짜')
    
    # 날짜를 datetime으로 변경
    df.index = pd.to_datetime(df.index)
    
    # 종목 이름 추출 및 종가 열 이름 변경
    name = df['이름'].iloc[0]
    df = df['종가'].rename(name)

    return df

def get_tickers():
    # 중복 제거 및 필요한 정보만 가져오도록 SQL 쿼리를 수정
    cursor.execute("SELECT DISTINCT ticker FROM stock_data")
    rows = cursor.fetchall()

    # 결과를 바로 데이터프레임으로 변환
    df = pd.DataFrame(rows, columns=['코드'])

    return df


def get_all_stock_prices(conn):
    query = "SELECT ticker, 날짜, 이름, 종가 FROM stock_data"
    
    # SQL 쿼리 결과를 바로 pandas 데이터프레임으로 읽어옴
    df = pd.read_sql(query, conn, parse_dates=['날짜'])

    # 데이터프레임을 피벗하여 각 종목별 종가 데이터를 열로 만듦
    prices_df = df.pivot(index='날짜', columns='이름', values='종가')

    return prices_df

def get_pbr(conn):
    query = "SELECT ticker, 날짜, 이름, PBR FROM stock_data"
    
    # SQL 쿼리 결과를 바로 pandas 데이터프레임으로 읽어옴
    df = pd.read_sql(query, conn, parse_dates=['날짜'])

    # 데이터프레임을 피벗하여 각 종목별 PBR 데이터를 열로 만듦
    pbr_df = df.pivot(index='날짜', columns='이름', values='PBR')

    return pbr_df