import pandas as pd
import numpy as np

class DBUpdater():
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
        #drop duplicates and choose most clicked
        pass

    @staticmethod
    def prepare_items_csv():
        all_items = pd.read_csv(item_path)
        del all_items['clicked']
        del all_items['viewed']
        DBUpdater.merge_two_df(from_takhlis, all_items)

    @staticmethod
    def remove_duplicates(new_df):
        existing_items =pd.read_csv('items.csv')
        for ad in new_df.iterrows():
            pass


        pass

