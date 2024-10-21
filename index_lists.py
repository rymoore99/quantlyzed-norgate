import norgatedata
import os
import pandas as pd
import pandas_ta as ta
import datetime, csv
import glob

databasename = 'US Equities'
#symbols = norgatedata.database_symbols(databasename)
allwatchlistnames = norgatedata.watchlists()

for wl in allwatchlistnames:
    wlk = norgatedata.watchlist(wl)
    nm = wl.replace(' ', '_').replace('&', 'and')
    pd.DataFrame.from_dict(wlk).to_csv(f"Z:\\symbol_lists\\{nm}.csv")

