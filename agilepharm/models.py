from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from datetime import datetime, date

    
    
class Store(models.Model):

    CATEGORY_CHOICES = [
        ('pain-relief', 'Pain Relief'),
        ('vitamins', 'Vitamins & Supplements'),
        ('skin', 'Skin & Beauty'),
        ('devices', 'Health Devices'),
        ('Prescription', 'Prescription Refills'),
        ('Nature', 'Field Supplements'),
        ('WholeShield', 'WholeShield Supplements'),
        ('medical', 'Medical Supplies'),
        ('Surgicals', 'Surgicals'),
    ]

    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    in_stock = models.BooleanField(default=True)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    publish_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

