import norgatedata
import os
import datetime, csv
from util.slack_sender import SlackSender
import sentry_sdk
from sentry_sdk import capture_exception
from dotenv import load_dotenv
import pandas_ta as ta

load_dotenv()
slack = SlackSender()

FULL = False

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN']
)
slack.post_message('Starting SP1500 load')
try:
    #databasename = 'US Equities'
    #symbols = norgatedata.database_symbols(databasename)
    #allwatchlistnames = norgatedata.watchlists()

    symbols = norgatedata.watchlist('S&P Composite 1500 Current & Past')

    ct = 1
    tm = datetime.datetime.now()

    sp1500_dir = 'Z:\\sp1500\\'

    #symbols = []
    symbols.append({
        'symbol': 'SPY',
        'securityname': 'SP 500 Index'
    })

    for symbol in symbols:
        try:
            priceadjust = norgatedata.StockPriceAdjustmentType.TOTALRETURN
            padding_setting = norgatedata.PaddingType.NONE

            fn1 = f'{sp1500_dir}pre_2024\\{symbol["symbol"]}.csv'
            fn2 = f'{sp1500_dir}post_2024\\{symbol["symbol"]}.csv'

            if FULL:
                start_date = '1995-01-01'
            else:
                start_date = '2023-01-01' # giving a year buffer for calcs

            timeseriesformat = 'pandas-dataframe'

            df_sym = norgatedata.price_timeseries(
                symbol['symbol'],
                stock_price_adjustment_setting = priceadjust,
                padding_setting = padding_setting,
                start_date = start_date,
                timeseriesformat=timeseriesformat,
            )
            df_sym['symbol'] = symbol["symbol"] # .replace('$', 'IDX_')
            df_sym['name'] = symbol["securityname"]

            if not 'Unadjusted Close' in df_sym.columns:
                df_sym['Unadjusted Close'] = ''
            if not 'Dividend' in df_sym.columns:
                df_sym['Dividend'] = ''

            if len(df_sym) > 90:
               # df_sym.set_index(pd.DatetimeIndex(df_sym["Date"]), inplace=True)
                df_sym['rsi'] = df_sym.ta.rsi()
                df_sym['rsi_3'] = df_sym.ta.rsi(length=3)
                df_sym['mom'] = df_sym.ta.mom()
                df_sym['ema'] = df_sym.ta.ema()
                df_sym['dema'] = df_sym.ta.dema()
                df_sym['apo'] = df_sym.ta.apo()
                df_sym['natr'] = df_sym.ta.natr()
                df_sym['adx_7'] = df_sym.ta.adx(length=7)['ADX_7']
                df_sym['sma_25'] = df_sym.ta.sma(len=25)
                df_sym['sma_50'] = df_sym.ta.sma(len=50)
                df_sym['sma_150'] = df_sym.ta.sma(len=150)

                print(f'{ct} / {len(symbols)}: {symbol} ')
                ct += 1

                numeric_cols = df_sym.select_dtypes(include='number').columns

                # Convert numeric columns to float
                df_sym[numeric_cols] = df_sym[numeric_cols].astype(float)

                df_sym = df_sym.round(decimals=2)
                df_sym = df_sym[["Open", "High", "Low", "Close", "Volume", "Turnover", "Unadjusted Close", "Dividend", "symbol", "name", "rsi", "rsi_3", "mom", "ema", "apo", "natr", 'adx_7', 'sma_25', 'sma_50', 'sma_150']]

            if FULL:
                df_sym.reset_index().query('Date<"1/1/2024"').to_csv(fn1, quoting=csv.QUOTE_NONNUMERIC, mode='w')

            df_sym.reset_index().query('Date>="1/1/2024"').to_csv(fn2, quoting=csv.QUOTE_NONNUMERIC, mode='w')
        except Exception as e:
            print(symbol, e)

    slack.post_message(f"finished in {datetime.datetime.now() - tm}")
except Exception as e:
    capture_exception(e)