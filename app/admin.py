from django.contrib import admin
from .models import Order  # Import your custom models here

# Register your custom models here
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('passenger_name', 'user', 'arrival_date', 'departure_date')


# Register your models here.

