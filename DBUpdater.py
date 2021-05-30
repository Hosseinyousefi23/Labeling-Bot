import pandas as pd
import numpy as np

class DBUpdater():
    all_items_path = 'all_items.csv'
    items_path = 'items.csv'
    @staticmethod
    def call_native_api(from_date=10, to_date=1):
        from datetime import datetime, timedelta
        FROM_DATE = datetime.now() - timedelta(days=from_date)
        TO_DATE = datetime.now() - timedelta(days=to_date)
        DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
        import requests

        TAKHLIS_TOKEN = 'Token c9eebadd825d461e6fc7751594671a558794f9d3'
        response = requests.get(('https://takhlis.yektanet.com/api/v2/summaries/?type=native&values=clicked,viewed' +
                                 '&group_by=ad_id' +
                                 '&start=%s' +
                                 '&end=%s') % (FROM_DATE.strftime(DATETIME_FORMAT), TO_DATE.strftime(DATETIME_FORMAT)),
                                headers={'Authorization': TAKHLIS_TOKEN, })
        data_old = response.json()['results']
        return(pd.DataFrame(data_old))

    @staticmethod
    def save_all_items(item_path='all_items.csv'): #this function saves a fucking 70 meg csv file which contains all ads /// It should be called every 5 days 
        import psycopg2
        import pandas as pd
        import logging

        ITEM_POSTGRES = { #These should become defined on the server
            'host': '',
            'database': '',
            'user': '',
            'password': '',
        }

        con = psycopg2.connect(host=ITEM_POSTGRES['host'],
                               database=ITEM_POSTGRES['database'],
                               user=ITEM_POSTGRES['user'],
                               password=ITEM_POSTGRES['password'])
        cur = con.cursor()
        cur.execute('select * from ads_data;')

        items = cur.fetchall()
        print('writing items...')
        pd.DataFrame(items,
                     columns=['id', 'title', 'created_at', 'image', 'campaign_id', 'campaign_title',
                              'advertiser_id',
                              'advertiser_name', 'viewed', 'clicked']).to_csv(item_path, index=False)
        items = None #Free up ram's space
    @staticmethod
    def merge_two_df(from_takhlis,all_items_csv): # what ever you can solve with naming . do not solve with comment

        new_items_df = pd.merge(from_takhlis,all_items_csv, how='inner', on='ad_id')
        return(new_items_df)


    @staticmethod
    def prepare_items_csv():
        all_items = pd.read_csv(DBUpdater.all_items_path)
        del all_items['clicked']
        del all_items['viewed']
        from_takhlis = DBUpdater.call_native_api()
        new_items = DBUpdater.merge_two_df(from_takhlis, all_items)
        new_items = DBUpdater.remove_duplicates(new_items)
        new_items.to_csv(DBUpdater.items_path)

    @staticmethod
    def remove_duplicates(new_df):
        existing_items =pd.read_csv(DBUpdater.items_path, index_col=0)
        start_index = len(existing_items)
        appened_items = existing_items.append(new_df,ignore_index=True)
        unique_items = appened_items.drop_duplicates(subset=["ad_title", "image"], keep="first")
        most_clicked = unique_items[unique_items.clicked>100]
        return(most_clicked)
