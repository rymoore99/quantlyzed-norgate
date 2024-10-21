import norgatedata
import os
import pandas as pd
import pandas_ta as ta
import datetime, csv
import glob
from slack_sender import SlackSender
import sentry_sdk
from sentry_sdk import capture_exception
from dotenv import load_dotenv, find_dotenv

load_dotenv()
slack = SlackSender()

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
    # files = glob.glob(os.path.join(sp1500_dir, '*'))
    #
    # # Loop through each file and delete it
    # for file in files:
    #     try:
    #         os.remove(file)
    #         print(f'{file} has been deleted.')
    #     except Exception as e:
    #         print(f'Error deleting {file}: {e}')

    for symbol in symbols:
        try:
            fn = f'{sp1500_dir}{symbol["symbol"]}.csv'

            #if os.path.isfile(fn):
             #   continue

            priceadjust = norgatedata.StockPriceAdjustmentType.TOTALRETURN
            padding_setting = norgatedata.PaddingType.NONE
            start_date = '1995-01-01'
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
                #df_sym['rsi_5'] = df_sym.ta.rsi(length=5)
                df_sym['mom'] = df_sym.ta.mom()
                df_sym['ema'] = df_sym.ta.ema()
                df_sym['dema'] = df_sym.ta.dema()
                df_sym['apo'] = df_sym.ta.apo()
                df_sym['natr'] = df_sym.ta.natr()
                #df_sym['slope'] = df_sym.ta.slope()
                #df_sym['slope_5'] = df_sym.ta.slope(length=5)

                print(f'{ct} / {len(symbols)}: {symbol} ')
                ct += 1

                numeric_cols = df_sym.select_dtypes(include='number').columns

                # Convert numeric columns to float
                df_sym[numeric_cols] = df_sym[numeric_cols].astype(float)

                df_sym = df_sym.round(decimals=2)
                df_sym = df_sym[["Open", "High", "Low", "Close", "Volume", "Turnover", "Unadjusted Close", "Dividend", "symbol", "name", "rsi", "mom", "ema", "apo", "natr"]]

            df_sym.to_csv(fn, quoting=csv.QUOTE_NONNUMERIC, mode='w')
        except Exception as e:
            print(symbol, e)

    slack.post_message(f"finished in {datetime.datetime.now() - tm}")
except Exception as e:
    capture_exception(e)