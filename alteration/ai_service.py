from datetime import datetime, timedelta
import random

class AlterationPredictor:
    # Simple rule-based prediction (can be replaced with ML model)
    OUTFIT_TIMES = {
        'Bridal': 7,  # days
        'Lehenga': 5,
        'Suit': 3,
        'Dress': 2,
        'Blouse': 1,
    }
    
    TAILOR_EFFICIENCY = {
        'experienced': 0.8,  # 20% faster
        'standard': 1.0,
        'new': 1.3,  # 30% slower
    }
    
    def predict_pickup_date(self, outfit_type, tailor_id=None):
        base_days = self.OUTFIT_TIMES.get(outfit_type, 3)
        
        # Add tailor efficiency factor
        if tailor_id:
            # Simple efficiency based on tailor specialties
            efficiency = self.TAILOR_EFFICIENCY['standard']
        else:
            efficiency = self.TAILOR_EFFICIENCY['standard']
        
        # Add some randomness for complexity
        complexity_factor = random.uniform(0.8, 1.2)
        
        total_days = int(base_days * efficiency * complexity_factor)
        pickup_date = datetime.now().date() + timedelta(days=total_days)
        
        return pickup_date, min(0.9, 0.7 + (0.2 * random.random()))