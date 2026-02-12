import pandas as pd
from django.core.management.base import BaseCommand
from forecasting.services import DemandForecaster

class Command(BaseCommand):
    help = 'Train demand forecasting models'

    def handle(self, *args, **options):
        # Load exported data
        try:
            df = pd.read_csv('sales_data.csv')
            self.stdout.write(f'Loaded {len(df)} records')
        except FileNotFoundError:
            self.stdout.write('Run export_sales_data first')
            return
        
        # Initialize and train forecaster
        forecaster = DemandForecaster()
        prepared_data = forecaster.prepare_data(df)
        
        # Train models
        forecaster.train_prophet(prepared_data)
        mae = forecaster.train_xgboost(prepared_data)
        
        # Save models
        forecaster.save_models()
        
        self.stdout.write(f'Models trained successfully. XGBoost MAE: {mae:.2f}')