from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    passenger_name = models.CharField(max_length=255)
    passenger_age = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    hotel_name = models.CharField(max_length=255)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    rooms = models.IntegerField()
    adults = models.IntegerField()
    children = models.IntegerField()
    flying_from = models.CharField(max_length=255)
    flying_to = models.CharField(max_length=255)
    airline = models.CharField(max_length=255)
    travel_class = models.CharField(max_length=255)
    additional_passenger_name = models.CharField(max_length=255, null=True, blank=True)
    additional_passenger_age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.passenger_name}"
    

