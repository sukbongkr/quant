import requests as rq
from bs4 import BeautifulSoup as bs
import re
from io import BytesIO
import pandas as pd
import numpy as np

def get_business_date():
    url = 'https://finance.naver.com/sise/sise_deposit.nhn'

    data = rq.get(url)
    data_html = bs(data.content, features="lxml")

    parse_day = data_html.select_one('div.subtop_sise_graph2 >ul.subtop_chart_note > li > span.tah').text


    busy_day = re.findall('[0-9]+', parse_day)
    busy_day = ''.join(busy_day)

    return busy_day

def get_kor_ticker():
    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    gen_otp_stk = {
        'mktId': 'STK',
        'trdDd': get_business_date(),
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
    }

    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
    otp_stk = rq.post(gen_otp_url, gen_otp_stk, headers=headers).text

    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_sector_stk = rq.post(down_url, {'code': otp_stk}, headers=headers)
    sector_stk = pd.read_csv(BytesIO(down_sector_stk.content), encoding='EUC-KR')

    gen_otp_ksq = {
        'mktId': 'KSQ',  # 코스닥 입력
        'trdDd': get_business_date(),
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03901'
    }
    otp_ksq = rq.post(gen_otp_url, gen_otp_ksq, headers=headers).text

    down_sector_ksq = rq.post(down_url, {'code': otp_ksq}, headers=headers)
    sector_ksq = pd.read_csv(BytesIO(down_sector_ksq.content), encoding='EUC-KR')

    krx_sector = pd.concat([sector_stk, sector_ksq]).reset_index(drop=True)
    krx_sector['종목명'] = krx_sector['종목명'].str.strip()
    krx_sector['기준일'] = get_business_date()

    gen_otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    gen_otp_data = {
        'searchType': '1',
        'mktId': 'ALL',
        'trdDd': get_business_date(),
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT03501'
    }
    headers = {'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
    otp = rq.post(gen_otp_url, gen_otp_data, headers=headers).text

    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    krx_ind = rq.post(down_url, {'code': otp}, headers=headers)

    krx_ind = pd.read_csv(BytesIO(krx_ind.content), encoding='EUC-KR')
    krx_ind['종목명'] = krx_ind['종목명'].str.strip()
    krx_ind['기준일'] = get_business_date()

    diff = list(set(krx_sector['종목명']).symmetric_difference(set(krx_ind['종목명'])))

    kor_ticker = pd.merge(krx_sector,
                        krx_ind,
                        on=krx_sector.columns.intersection(
                            krx_ind.columns).tolist(),
                        how='outer')



    kor_ticker['종목구분'] = np.where(kor_ticker['종목명'].str.contains('스팩|제[0-9]+호'), '스팩',
                                np.where(kor_ticker['종목코드'].str[-1:] != '0', '우선주',
                                        np.where(kor_ticker['종목명'].str.endswith('리츠'), '리츠',
                                                    np.where(kor_ticker['종목명'].isin(diff),  '기타',
                                                    '보통주'))))
    kor_ticker = kor_ticker.reset_index(drop=True)
    kor_ticker.columns = kor_ticker.columns.str.replace(' ', '')
    kor_ticker = kor_ticker[['종목코드', '종목명', '시장구분', '종가',
                            '시가총액', '기준일', 'EPS', '선행EPS', 'BPS', '주당배당금', '종목구분']]
    kor_ticker['시가총액'] = kor_ticker['시가총액'].apply(pd.to_numeric, errors='coerce')
    kor_ticker = kor_ticker.replace({np.nan: None})
    kor_ticker['기준일'] = pd.to_datetime(kor_ticker['기준일'])
    kor_ticker['기준일'] = kor_ticker['기준일'].astype(str)

    return kor_ticker

import sqlite3

con = sqlite3.connect('stock_db.sqlite3')

mycursor = con.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS kor_ticker
(
    종목코드 TEXT NOT NULL,
    종목명 TEXT,
    시장구분 TEXT,
    종가 REAL,
    시가총액 REAL,
    기준일 TEXT,
    EPS REAL,
    선행EPS REAL,
    BPS REAL,
    주당배당금 REAL,
    종목구분 TEXT,
    PRIMARY KEY(종목코드, 기준일)
);
"""

mycursor.execute(create_table_query)
con.commit()

query = f"""
    INSERT OR REPLACE INTO kor_ticker (종목코드,종목명,시장구분,종가,시가총액,기준일,EPS,선행EPS,BPS,주당배당금,종목구분)
    VALUES (?,?,?,?,?,?,?,?,?,?,?);
"""

kor_ticker = get_kor_ticker()
args = kor_ticker.astype({'시가총액': float}).values.tolist()

mycursor.executemany(query, args)
con.commit()

con.close()
