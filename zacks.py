import json
import time
import os
import urllib.request
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import sentry_sdk
from sentry_sdk import capture_exception
from util.db_util import get_local_cursor, insert_dict
from util.slack_sender import SlackSender

load_dotenv(find_dotenv())  # Load the .env file

slack = SlackSender()

sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN']
)
slack.post_message('Starting Zacks load')

class ZacksLoader():

    def __init__(self):
        c = ''

    def Zacks_Rank(self, Symbol):
        # Wait for 2 seconds
        time.sleep(0.2)
        url = 'https://quote-feed.zacks.com/index?t=' + Symbol
        downloaded_data = urllib.request.urlopen(url)
        data = downloaded_data.read()
        data_str = data.decode()

        j = json.loads(data_str)

        ret = {}

        try:
            for l in j[Symbol]:
                try:
                    if l != 'source':
                        ret[l] = j[Symbol][l]
                except:
                    print('ooops')
        except:
            print(Symbol)

        return ret

    def do_load(self):
        sql = f"SELECT * from quan_data_archive.list_sp_1500_all"
        cursor = get_local_cursor()
        cursor.execute(sql)

        syms = cursor.fetchall()
        ct = 1
        succ_ct = 0
        ranks = []
        for symbol in syms:
            try:
                s = symbol['symbol']
                if not '-' in s:
                    rank = self.Zacks_Rank(s)
                    print(ct, s)
                    ct += 1
                    rank['insert_date'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

                    if 'reason' in rank and rank['reason'] != 'Invalid ticker':
                        print(f'bad ticker: {s}')
                    else:
                        succ_ct += 1
                        ranks.append(rank)
                        insert_dict(rank, 'quan_data_archive.zacks', cursor)

            except Exception as e:
                capture_exception(e)

        # df = pd.DataFrame.from_dict(ranks)
        # df.to_csv(f'Z:\\zacks\\{formatted_date}.csv')
        cursor.connection.commit()

        return succ_ct

succ_ct = ZacksLoader().do_load()
slack.post_message(f'Loaded {succ_ct} Zacks stocks')