import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'passenger_name': ['exact', 'icontains'],
            'passenger_age': ['exact', 'gte', 'lte'],
            'phone_number': ['exact'],
            'hotel_name': ['exact', 'icontains'],
            'arrival_date': ['exact', 'gte', 'lte'],
            'departure_date': ['exact', 'gte', 'lte'],
            'rooms': ['exact', 'gte', 'lte'],
            'adults': ['exact', 'gte', 'lte'],
            'children': ['exact', 'gte', 'lte'],
            'flying_from': ['exact', 'icontains'],
            'flying_to': ['exact', 'icontains'],
            'airline': ['exact', 'icontains'],
            'travel_class': ['exact', 'icontains'],
        }
