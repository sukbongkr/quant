import json
import requests as rq
import pandas as pd
from ticker import get_business_date
import time
import json
import requests as rq
import pandas as pd
from tqdm import tqdm

sector_code = [
    'G25', 'G35', 'G50', 'G40', 'G10', 'G20', 'G55', 'G30', 'G15', 'G45'
]

data_sector = []

for i in tqdm(sector_code):
    url = f'''http://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={get_business_date()}&sec_cd={i}'''    
    data = rq.get(url).json()
    data_pd = pd.json_normalize(data['list'])

    data_sector.append(data_pd)

    time.sleep(2)

kor_sector = pd.concat(data_sector, axis = 0)
kor_sector = kor_sector[['IDX_CD', 'CMP_CD', 'CMP_KOR', 'SEC_NM_KOR']]
kor_sector['기준일'] = get_business_date()
kor_sector['기준일'] = pd.to_datetime(kor_sector['기준일'])

kor_sector['기준일'] = kor_sector['기준일'].astype(str)

import sqlite3

con = sqlite3.connect('stock_db.sqlite3')

mycursor = con.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS kor_sector
(
    IDX_CD TEXT NOT NULL,
    CMP_CD TEXT NOT NULL,
    CMP_KOR TEXT,
    SEC_NM_KOR TEXT,
    기준일 TEXT,
    PRIMARY KEY(CMP_CD, 기준일)
);
"""

mycursor.execute(create_table_query)
con.commit()

query = f"""
    INSERT OR REPLACE INTO kor_sector (IDX_CD, CMP_CD, CMP_KOR, SEC_NM_KOR, 기준일)
    VALUES (?,?,?,?,?);
"""

args = kor_sector.values.tolist()

mycursor.executemany(query, args)
con.commit()

con.close()