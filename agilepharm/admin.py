from django.contrib import admin
# Register your models here.
from . import models
from .models import Store
#from .models import Category, Product
    
#This model is for the fist carousel image
class StoreAdmin (admin.ModelAdmin):
    list_display = ['title','price','description']
admin.site.register(Store, StoreAdmin)
