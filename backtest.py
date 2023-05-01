import sqlite3
import pandas as pd
import bt
from matplotlib import pyplot as plt
from db import get_all_stock_prices, get_tickers, get_stock, get_pbr

#stock_data.db에 접속
conn = sqlite3.connect('stock_data.db')
cursor = conn.cursor()

# 데이터 로드 (종가 데이터와 PBR 데이터)
prices_df = get_all_stock_prices(conn)

pbr_df = get_pbr(conn)

# 분기별 기준 날짜 생성
quarterly_dates = pd.date_range(prices_df.index.min(), prices_df.index.max(), freq='Q')

# 낮은 PBR 주식 선택 함수
def get_low_pbr_stocks(pbr, quantile=0.1):
    return pbr.rank(pct=True).apply(lambda x: x <= quantile)

# 전략 클래스 정의
class LowPBR(bt.Algo):
    def __init__(self, pbr_df, rebalance_dates, quantile):
        self.pbr_df = pbr_df
        self.rebalance_dates = rebalance_dates
        self.quantile = quantile

    def __call__(self, target):
        if target.now in self.rebalance_dates:
            low_pbr_stocks = get_low_pbr_stocks(self.pbr_df.loc[target.now], self.quantile)
            target.temp['selected'] = low_pbr_stocks
        else:
            target.temp['selected'] = None
        return True

class WeighSelected(bt.Algo):
    def __init__(self, temp_key):
        self.temp_key = temp_key

    def __call__(self, target):
        selected = target.temp[self.temp_key]
        if selected is None:
            target.temp['weights'] = None
        else:
            target.temp['weights'] = selected / selected.sum()
        return True

# 전략 구성
strategy = bt.Strategy('LowPBR', [
    bt.algos.RunQuarterly(),
    LowPBR(pbr_df, quarterly_dates, 0.1),
    WeighSelected('selected'),
    bt.algos.Rebalance()
])

# 백테스트 수행
backtest = bt.Backtest(strategy, prices_df)
result = bt.run(backtest)

# 백테스트 결과 출력
result.plot(title='Low PBR Strategy Backtest')
plt.show()







