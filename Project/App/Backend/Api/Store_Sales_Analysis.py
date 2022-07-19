import pickle
import inflection
import pandas as pd
import numpy as np
import math
import datetime
import os

class Store_Sales_Analysis(object):
    
    def __init__(self):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        #self.home_path = 'A:\\Andrew\\Desenvolvimento\\Portfolio\\Store Sales Analysis\\Development\\Data\\'
        #\\ when in windows, / when in linux
        self.competition_distance_scaler   = self.load_scaler('/static/models/competition_distance_scaler')
        self.competition_time_month_scaler = self.load_scaler('/static/models/competition_time_month_scaler')
        self.promo_time_week_scaler        = self.load_scaler('/static/models/promo_time_week_scaler')
        self.year_scaler                   = self.load_scaler('/static/models/year_scaler')
        self.store_type_scaler             = self.load_scaler('/static/models/store_type_encoder')

    def load_scaler(self, scaler_name):
        #self.home_path
        scaler = pickle.load(open(self.current_path + scaler_name + '.pkl', 'rb'))
        return scaler

    def data_cleaning(self, df1): 
        
        ## Rename Columns
        cols_old = ['Store', 'DayOfWeek', 'Date', 'Open', 'Promo', 'StateHoliday', 'SchoolHoliday', 
                    'StoreType', 'Assortment', 'CompetitionDistance', 'CompetitionOpenSinceMonth',
                    'CompetitionOpenSinceYear', 'Promo2', 'Promo2SinceWeek', 'Promo2SinceYear', 'PromoInterval']
        
        snakecase = lambda x: inflection.underscore(x)
        
        cols_new = list(map(snakecase, cols_old))
        
        # rename
        df1.columns = cols_new
        
        ## Data Types
        df1['date'] = pd.to_datetime(df1['date'])
        
        ## Fill NA
        #competition_distance        
        df1['competition_distance'] = df1['competition_distance'].apply(lambda x: 200000.0 if math.isnan(x) else x)
        
        #competition_open_since_month
        df1['competition_open_since_month'] = \
            df1.apply(lambda x: x['date'].month if math.isnan(x['competition_open_since_month']) else x['competition_open_since_month'], axis=1)
            
        #competition_open_since_year 
        df1['competition_open_since_year'] = \
            df1.apply(lambda x: x['date'].year if math.isnan(x['competition_open_since_year']) else x['competition_open_since_year'], axis=1)
            
        #promo2_since_week           
        df1['promo2_since_week'] = \
            df1.apply(lambda x: x['date'].week if math.isnan(x['promo2_since_week']) else x['promo2_since_week'], axis=1)
            
        #promo2_since_year           
        df1['promo2_since_year'] = \
            df1.apply(lambda x: x['date'].year if math.isnan(x['promo2_since_year']) else x['promo2_since_year'], axis=1)
            
        #promo_interval              
        current_month = \
            {1: 'Jan',  2: 'Fev',  3: 'Mar',  4: 'Apr',  5: 'May',  6: 'Jun',  7: 'Jul',  8: 'Aug',  9: 'Sep',  10: 'Oct', 11: 'Nov', 12: 'Dec'}
            
        df1['current_month'] = df1['date'].dt.month.map(current_month)
        
        df1['promo_interval'].fillna(0, inplace=True)
        
        df1['active_promo'] = \
        df1[['promo_interval', 'current_month']]\
            .apply(lambda x: 0 if x['promo_interval'] == 0 else 1 if x['current_month'] in x['promo_interval'].split( ',' ) else 0, axis=1 )
        ## Change Data Types
        # competiton
        df1['competition_open_since_month'] = df1['competition_open_since_month'].astype('int64')
        df1['competition_open_since_year'] = df1['competition_open_since_year'].astype('int64')
        
        # promo2
        df1['promo2_since_week'] = df1['promo2_since_week'].astype('int64')
        df1['promo2_since_year'] = df1['promo2_since_year'].astype('int64')
        
        # Assortment Column
        df1['assortment'] = df1['assortment'].apply(lambda x: 'Basic' if x == 'a' else 'Extra' if x == 'b' else 'Extended')
        
        # State holiday Column
        df1['state_holiday'] = \
            df1['state_holiday'].apply(lambda x: 'Public' if x == 'a' else 'Easter' if x == 'b' else 'Christmas' if x == 'c' else 'Regular_Day')
        
        data_cleaning = df1
        
        return data_cleaning

    def feature_extraction(self, df2):
        
        df2['year'] = df2['date'].dt.year
        df2['month'] = df2['date'].dt.month
        df2['day'] = df2['date'].dt.day
        df2['week_of_year'] = df2['date'].dt.weekofyear
        
        df2['year_week'] = df2['date'].dt.strftime('%Y-%W')
        
        # competition since
        df2['competition_since'] = \
            df2.apply(lambda x: datetime.datetime(year=x['competition_open_since_year'], month=x['competition_open_since_month'],day=1), axis=1)
        df2['competition_time_month'] = \
            ((df2['date'] - df2['competition_since'])/30).apply(lambda x: x.days).astype(int)
            
        # promo since
        df2['promo_since'] = df2['promo2_since_year'].astype(str) + '-' + df2['promo2_since_week'].astype(str)
        df2['promo_since'] = df2['promo_since'].apply(lambda x: datetime.datetime.strptime(x + '-1', '%Y-%W-%w') - datetime.timedelta(days=7))
        df2['promo_time_week'] = ((df2['date'] - df2['promo_since'])/7).apply(lambda x: x.days).astype(int)
        
        ## Filtragem das Linhas
        # NOTE: Previously: df2 = df2[(df2['open'] != 0) & (df2['sales'] > 0)]
        # NOTE: Now: df2 = df2[df2['open'] != 0]
        # NOTE: Because the "sales" column doesn't exists since we're dealing with a test set
        # NOTE: The "sales" column equivalent will be the "prediction" column because we're PREDICTING the sales
        
        df2 = df2[df2['open'] != 0]
        
        ## Selecao das Colunas
        cols_drop = ['open', 'promo_interval', 'current_month']
        df2 = df2.drop(cols_drop, axis=1)
        
        feature_extraction = df2
        
        return feature_extraction

    def data_preparation(self, df3):
        
        ## Rescaling 
        # competition distance
        df3['competition_distance'] = self.competition_distance_scaler.fit_transform(df3[['competition_distance']].values)
        
        # competition time month
        df3['competition_time_month'] = self.competition_time_month_scaler.fit_transform(df3[['competition_time_month']].values)
        
        # promo time week
        df3['promo_time_week'] = self.promo_time_week_scaler.fit_transform(df3[['promo_time_week']].values)
        
        # year
        df3['year'] = self.year_scaler.fit_transform(df3[['year']].values)
        
        ### Encoding
        # state_holiday - One Hot Encoding
        df3 = pd.get_dummies(df3, prefix=['state_holiday'], columns=['state_holiday'])
        
        # store_type - Label Encoding
        df3['store_type'] = self.store_type_scaler.fit_transform(df3['store_type'])
        
        # assortment - Ordinal Encoding
        assortment_dict = {'Basic': 1, 'Extra': 2, 'Extended': 3}
        df3['assortment'] = df3['assortment'].map(assortment_dict)
        
        # day 
        df3['day_sin'] = df3['day'].apply(lambda x: np.sin(x * (2. * np.pi/30)))
        df3['day_cos'] = df3['day'].apply(lambda x: np.cos(x * (2. * np.pi/30)))
        
        # day of week
        df3['day_of_week_sin'] = df3['day_of_week'].apply(lambda x: np.sin(x * (2. * np.pi/7)))
        df3['day_of_week_cos'] = df3['day_of_week'].apply(lambda x: np.cos(x * (2. * np.pi/7)))
        
        # month
        df3['month_sin'] = df3['month'].apply(lambda x: np.sin(x * (2. * np.pi/12)))
        df3['month_cos'] = df3['month'].apply(lambda x: np.cos(x * (2. * np.pi/12)))
        
        # week of year
        df3['week_of_year_sin'] = df3['week_of_year'].apply(lambda x: np.sin(x * (2. * np.pi/52)))
        df3['week_of_year_cos'] = df3['week_of_year'].apply(lambda x: np.cos(x * (2. * np.pi/52)))
        
        cols_selected = [ 'store', 'promo', 'store_type', 'assortment', 'competition_distance', 
            'competition_open_since_month', 'competition_open_since_year', 'promo2', 'promo2_since_week',
            'promo2_since_year', 'competition_time_month', 'promo_time_week', 'day_of_week_sin',
            'day_of_week_cos', 'month_sin', 'month_cos', 'day_sin', 'day_cos', 'week_of_year_sin',
            'week_of_year_cos', 'year']
        
        data_preparation = df3[cols_selected]
        
        return data_preparation
    
    def get_prediction(self, model, original_data, test_data):
        # prediction
        
        pred = model.predict(test_data)
        
        # join pred into the original data
        original_data['prediction'] = np.expm1(pred)
        # convert to json
        
        prediction = original_data.to_json(orient='records', date_format='iso')
        
        return prediction