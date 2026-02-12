from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from core.models import Category
from .models import DemandForecast
from .services import DemandForecaster
import os

@api_view(['POST'])
def generate_forecast(request):
    """Generate demand forecast for next month"""
    forecaster = DemandForecaster()
    
    if not os.path.exists('forecasting_models.pkl'):
        return Response({'error': 'Models not trained. Run train_models command first.'}, status=400)
    
    forecaster.load_models()
    
    # Get next month date
    next_month = datetime.now().replace(day=1) + timedelta(days=32)
    next_month = next_month.replace(day=1)
    
    forecasts = []
    categories = Category.objects.all()
    sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']  # Common sizes
    
    for category in categories:
        for size in sizes:
            try:
                demand, confidence = forecaster.predict_demand(category.name, size, next_month)
                
                # Save to database
                forecast, created = DemandForecast.objects.update_or_create(
                    category=category,
                    size=size,
                    forecast_month=next_month,
                    defaults={
                        'predicted_demand': demand,
                        'confidence_score': confidence
                    }
                )
                
                forecasts.append({
                    'category': category.name,
                    'size': size,
                    'predicted_demand': demand,
                    'confidence_score': round(confidence, 2)
                })
            except Exception as e:
                continue
    
    return Response({'forecasts': forecasts})

@api_view(['GET'])
def get_forecasts(request):
    """Get existing forecasts"""
    forecasts = DemandForecast.objects.select_related('category').order_by('-created_at')[:50]
    
    data = [{
        'category': f.category.name,
        'size': f.size,
        'predicted_demand': f.predicted_demand,
        'confidence_score': f.confidence_score,
        'forecast_month': f.forecast_month
    } for f in forecasts]
    
    return Response({'forecasts': data})