from django.db import models
from core.models import Category

class DemandForecast(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    predicted_demand = models.IntegerField()
    forecast_month = models.DateField()
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['category', 'size', 'forecast_month']

    def __str__(self):
        return f"{self.category.name} {self.size} - {self.predicted_demand}"