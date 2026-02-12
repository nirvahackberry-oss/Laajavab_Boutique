import pandas as pd
import pickle
from datetime import datetime, timedelta
from prophet import Prophet
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

class DemandForecaster:
    def __init__(self):
        self.prophet_model = None
        self.xgb_model = None
        self.label_encoders = {}
        
    def prepare_data(self, df):
        # Aggregate daily sales by category and size
        df['order_date'] = pd.to_datetime(df['order_date'])
        daily_sales = df.groupby(['order_date', 'category', 'size'])['quantity'].sum().reset_index()
        
        # Encode categorical variables
        for col in ['category', 'size']:
            le = LabelEncoder()
            daily_sales[f'{col}_encoded'] = le.fit_transform(daily_sales[col])
            self.label_encoders[col] = le
            
        return daily_sales
    
    def train_prophet(self, df):
        # Prophet expects 'ds' and 'y' columns
        prophet_data = df.groupby('order_date')['quantity'].sum().reset_index()
        prophet_data.columns = ['ds', 'y']
        
        self.prophet_model = Prophet(yearly_seasonality='auto', weekly_seasonality='auto')
        self.prophet_model.fit(prophet_data)
        
    def train_xgboost(self, df):
        # Features: category, size, month, day_of_week, price
        df['month'] = df['order_date'].dt.month
        df['day_of_week'] = df['order_date'].dt.dayofweek
        
        features = ['category_encoded', 'size_encoded', 'month', 'day_of_week']
        X = df[features]
        y = df['quantity']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
        self.xgb_model.fit(X_train, y_train)
        
        # Calculate accuracy
        y_pred = self.xgb_model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        return mae
    
    def predict_demand(self, category, size, forecast_date):
        # Prophet prediction for overall trend
        if self.prophet_model is None or self.xgb_model is None:
            raise ValueError("Models must be trained before making predictions. Call train_prophet() and train_xgboost() first.")
        
        future_df = pd.DataFrame({'ds': [forecast_date]})
        prophet_forecast = self.prophet_model.predict(future_df)
        trend_factor = prophet_forecast['yhat'].iloc[0]
        
        # XGBoost prediction for category/size specific demand
        category_encoded = self.label_encoders['category'].transform([category])[0]
        size_encoded = self.label_encoders['size'].transform([size])[0]
        
        features = [[category_encoded, size_encoded, forecast_date.month, forecast_date.weekday()]]
        xgb_prediction = self.xgb_model.predict(features)[0]
        
        # Combine predictions
        final_prediction = max(1, int(xgb_prediction * (trend_factor / 10)))
        confidence = min(0.9, prophet_forecast['yhat_upper'].iloc[0] / prophet_forecast['yhat'].iloc[0])
        
        return final_prediction, confidence
    
    def save_models(self, filepath='forecasting_models.pkl'):
        models = {
            'prophet': self.prophet_model,
            'xgb': self.xgb_model,
            'encoders': self.label_encoders
        }
        with open(filepath, 'wb') as f:
            pickle.dump(models, f)
    
    def load_models(self, filepath='forecasting_models.pkl'):
        with open(filepath, 'rb') as f:
            models = pickle.load(f)
        self.prophet_model = models['prophet']
        self.xgb_model = models['xgb']
        self.label_encoders = models['encoders']