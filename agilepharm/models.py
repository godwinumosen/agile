from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from datetime import datetime, date



class Store(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='products/')
    in_stock = models.BooleanField(default=True) 
    author_category = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_date = models.DateTimeField (auto_now_add= True)

    class Meta:
        ordering =['-publish_date']

    def __str__(self):
        return self.title
