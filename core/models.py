from django.db import models
from django.contrib.auth.models import User

class SoilData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    temperature = models.FloatField()
    recommended_crop = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True) 
    is_saved = models.BooleanField(default=False) 

    def __str__(self):
        return f"{self.user.username} - {self.recommended_crop} ({self.date.date()})" if self.user else "Guest"
