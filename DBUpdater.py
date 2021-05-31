import pandas as pd
import numpy as np
import os
import psycopg2
import pandas as pd

class DBUpdater():
    all_items_path = 'all_items.csv'
    items_path = 'items.csv'
    @staticmethod
    def call_native_api(from_date=5, to_date=1):
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
        df = pd.DataFrame(data_old)
        df.columns = ['id','viewed','clicked']
        return(df)

    @staticmethod
    def save_all_items(item_path='all_items.csv'): #this function saves a fucking 70 meg csv file which contains all ads /// It should be called every 5 days 

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
        new_items_df = pd.merge(from_takhlis,all_items_csv, how='inner', on='id')
        return(new_items_df)


    @staticmethod
    def prepare_items_csv(start=5, end=1):
        all_items = pd.read_csv(DBUpdater.all_items_path)
        del all_items['clicked']
        del all_items['viewed']
        from_takhlis = DBUpdater.call_native_api(from_date=start, to_date=end )
        new_items = DBUpdater.merge_two_df(from_takhlis, all_items)
        new_items = DBUpdater.remove_duplicates(new_items)
        if os.path.isfile(DBUpdater.items_path):
            existing_items = pd.read_csv(DBUpdater.items_path, index_col=0)
            new_items = existing_items.append(new_items,ignore_index=True)
        new_items.to_csv(DBUpdater.items_path)

    @staticmethod
    def remove_duplicates(new_df):
        if os.path.isfile(DBUpdater.items_path):
            existing_items =pd.read_csv(DBUpdater.items_path, index_col=0)
        else:
            existing_items = pd.DataFrame([],columns=new_df.columns)
        start_index = len(existing_items)
        appened_items = existing_items.append(new_df,ignore_index=True)
        unique_items = appened_items.drop_duplicates(subset=["title", "image"], keep="first")
        new_ones = unique_items.iloc[start_index: , :]
        most_clicked = new_ones[new_ones.clicked>500]
        return(most_clicked)
