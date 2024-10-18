from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# Remove the incorrect import
# from django import Order

from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    #additional_passengers_count = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Order
        fields = ['passenger_name', 'passenger_age', 'phone_number', 'hotel_name', 
                  'arrival_date', 'departure_date', 'rooms', 'adults', 'children', 
                  'flying_from', 'flying_to', 'airline', 'travel_class']


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
