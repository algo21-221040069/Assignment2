from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from QUANTAXIS import QA_Performance, MARKET_TYPE, QA_User, ORDER_DIRECTION, QA_Risk, QA_fetch_cryptocurrency_day_adv
from matplotlib import pyplot as plt
from tqdm import tqdm

from backtest.strategy import NeuralQuantStrategy
from backtest.tools import evaluate_pnl
from settings import CRYPTO_TEST_CREDENTIALS, BACKTEST_DIR
from utilities.visualizations import display_trading_data


class BasePaperTrader:
    def init_account(self, init_cash, credentials, market_type=MARKET_TYPE.CRYPTOCURRENCY):
        username = credentials['username']
        pwd = credentials['pwd']
        portfolio_name = credentials['portfolio_name']
        account_name = credentials['account_name']

        self.user = QA_User(username=username, password=pwd)
        account = self.user.get_account(portfolio_cookie=portfolio_name, account_cookie=account_name)
        if account is None:
            portfolio = self.user.get_portfolio(portfolio_cookie=portfolio_name)
            account = portfolio.new_account(
                account_cookie=account_name,
                market_type=market_type,
                init_cash=init_cash,
            )
        self.account = account

    def __init__(self, init_cash=10_000, credentials=CRYPTO_TEST_CREDENTIALS, market_type=MARKET_TYPE.CRYPTOCURRENCY,
                 commission_rate=1e-3, tax_rate=0):
        self.init_account(init_cash=init_cash, credentials=credentials, market_type=market_type)
        self.commission_rate = commission_rate
        self.tax_rate = tax_rate

    def buy(self, asset_code, price, time, amount: float = None, verbose=True):
        if amount is None:
            if self.account.market_type == MARKET_TYPE.STOCK_CN:
                amount = self.account.cash_available / price // 100 * 100
            if self.account.market_type == MARKET_TYPE.CRYPTOCURRENCY:
                amount = self.account.cash_available // (price * (1 + self.commission_rate))

        result = self.account.receive_simpledeal(
            code=asset_code,
            trade_price=price,
            trade_amount=amount,
            trade_towards=ORDER_DIRECTION.BUY,
            trade_time=time
        )
        if result != -1 and verbose:
            print(f'[SIGNAL] ??????{asset_code} ?????????{price:,.2f} ?????????{amount:.4f} ??????: {self.account.cash_available:,.2f}')
        return result == 0

    def sell(self, asset_code, price, time, amount: float = None, verbose=True):
        available = self.account.hold_available.get(asset_code)
        if available is None:
            return
        if amount is None:
            amount = available
        amount = min(amount, available)
        result = self.account.receive_simpledeal(
            code=asset_code,
            trade_price=price,
            trade_amount=amount,
            trade_towards=ORDER_DIRECTION.SELL,
            trade_time=time
        )
        if result != -1 and verbose:
            print(f'[SIGNAL] ??????{asset_code} ?????????{price:,.2f} ?????????{amount:.4f} ??????: {self.account.cash_available:,.2f}')
        return result == 0


def paper_trade(symbol, data, trader, weight_file, history_size, future_size, strategy_params=None):
    strategy = NeuralQuantStrategy(weight_file, params=strategy_params)
    print(f"???{strategy.name_cn}???")
    print(f"???????????????...")
    data = strategy.construct_data(data).dropna()
    print(f"????????????????????????: {symbol}")

    window_size = history_size + future_size
    previous_action = None
    length = len(data) - window_size + 1
    for i in tqdm(range(0, length), total=length):
        segment = data.iloc[i: i + window_size].copy()
        bar = segment.iloc[history_size - 1]
        time = segment.index[history_size - 1] \
            if isinstance(segment.index[history_size], pd.Timestamp) \
            else segment.index[history_size - 1][0]

        # disp = time > datetime.strptime("2021-07-20", '%Y-%m-%d')

        action = strategy.on_data(segment, symbol, previous_action, history_size=history_size)
        if trader.account.hold_available.get(symbol) is None:
            if action == 'BUY':
                all_in = trader.account.cash_available // (bar.close * (1 + trader.commission_rate))
                success = trader.buy(asset_code=symbol, price=bar.close, amount=all_in, time=time)
                if not success:
                    print(all_in, bar.close, trader.account.cash_available)
                previous_action = action
        else:
            if action == 'SELL':
                trader.sell(asset_code=symbol, price=bar.close, time=time)
                previous_action = None

    print(f"????????????, ???????????????{trader.account.cash_available:,.2f}")
    print(f"??????: {trader.account.hold_available}")
    performance = QA_Performance(trader.account)
    pnl_df = performance.pnl
    assert isinstance(pnl_df, pd.DataFrame)
    return pnl_df


def inspect_report(file_name: str = None, pattern: str = None, commission_rate=1e-3, tax_rate=1e-3, display=True):
    import QUANTAXIS as qa

    if file_name is not None:
        if not Path(file_name).exists():
            file_path = BACKTEST_DIR / file_name
        else:
            file_path = file_name
    else:
        file_path = list(BACKTEST_DIR.rglob(pattern))[0]
    pnl = pd.read_csv(str(file_path))
    report = evaluate_pnl(pnl, commission_rate, tax_rate)
    for key, val in report.items():
        if key.startswith('??????'):
            continue
        if key.endswith('???'):
            val = f"{val * 100:.2f}%"
        if isinstance(val, np.float):
            val = f"{val:.2f}"
        print(f"{key}: {val}")
    print('===\n')

    risk = evaluate_risk(file_path)
    print(f"????????????: {risk.max_dropback * 100:.2f}%")

    if not display:
        return

    risk.plot_assets_curve()
    plt.show()

    returns = pnl['true_ratio']
    max_return = returns.max()
    min_return = returns.min()
    returns.plot.hist(bins=len(returns), xlim=[min_return * 2, max_return * 2], title='???????????????')
    plt.show()

    for i, (index, row) in enumerate(pnl.iterrows()):
        opendate = datetime.strptime(row.opendate, '%Y-%m-%d %H:%M:%S')
        closedate = datetime.strptime(row.closedate, '%Y-%m-%d %H:%M:%S')

        if isinstance(row.code, int):
            symbol = f"{row.code:06d}"
            start_date = opendate - timedelta(days=120)
            end_date = closedate + timedelta(days=20)
            data = qa.QA_fetch_stock_day_adv(symbol, start=start_date, end=end_date).to_qfq().data
        else:
            symbol = row.code
            start_date = opendate - timedelta(days=5)
            end_date = closedate + timedelta(days=5)
            data = qa.QA_fetch_cryptocurrency_min_adv(symbol, str(start_date), str(end_date),
                                                      frequence='60min').data.dropna()
        # data = indicator_MA(data, 5, 10)
        # data = indicator_MACD(data, )
        # data = indicator_KDJ(data)

        title = f"{closedate - opendate} ?????????: {row.true_ratio * 100:.2f}%"
        display_trading_data(data, pointers=[opendate, closedate], title=title)


def compare_reports(pattern, commission_rate=1e-3, tax_rate=1e-3):
    target_files = sorted(BACKTEST_DIR.rglob(pattern))
    summary_path = BACKTEST_DIR / 'summary_atr.csv'
    reports = []
    for report_file in target_files:
        pnl = pd.read_csv(str(report_file))
        reports.append(evaluate_pnl(pnl, commission_rate, tax_rate))

    indices = [p.stem for p in target_files]
    summary = pd.DataFrame(reports, index=indices)
    summary.T.to_csv(str(summary_path), encoding='utf-8-sig')


def evaluate_risk(records_file, benchmark='BINANCE.BTCUSDT'):
    if not Path(str(records_file)).exists():
        records_path = BACKTEST_DIR / str(records_file)
        if not records_path.exists():
            raise FileNotFoundError(f"Trade record file {str(records_file)}")
    else:
        records_path = records_file
    table = pd.read_csv(str(records_path))
    # opendate = table['opendate'].apply(lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
    # closedate = table['closedate'].apply(lambda s: datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
    # # start_time = opendate.min()
    # # end_time = closedate.max()
    trader = BasePaperTrader(init_cash=1_000_000)
    for index, row in table.iterrows():
        opendate = row['opendate']
        closedate = row['closedate']
        symbol = row['code']
        buy_price = row['buy_price']
        amount = row['amount']
        sell_price = row['sell_price']
        trader.buy(asset_code=symbol, price=buy_price, time=opendate, amount=amount, verbose=False)
        trader.sell(asset_code=symbol, price=sell_price, time=closedate, verbose=False)

    start_date = datetime.strptime(trader.account.start_date, "%Y-%m-%d") + timedelta(hours=8)
    end_date = datetime.strptime(trader.account.end_date, "%Y-%m-%d") + timedelta(hours=24)
    market_data = QA_fetch_cryptocurrency_day_adv(symbol, start=start_date, end=end_date)
    risk = QA_Risk(
        trader.account,
        benchmark_code=benchmark,
        benchmark_type=MARKET_TYPE.CRYPTOCURRENCY,
        market_data=market_data
    )
    return risk
