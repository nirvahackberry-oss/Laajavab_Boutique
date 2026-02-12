from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=10, unique=True, help_text="e.g., BR, CW, FW")

    def __str__(self):
        return f"{self.name} ({self.prefix})"

class OutfitType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="e.g., LHG, SRE, GWN")

    def __str__(self):
        return f"{self.name} ({self.code})"
