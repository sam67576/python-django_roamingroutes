from django.contrib import admin
from django.urls import path
from app.views import first,index, aboutus, register, loginpage, logoutUser, mytrips ,book, bookingfl ,bookform , payment_success ,final_view,packages ,TemplateView ,pdf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', first, name='first'),
    path('index/', index, name='home'),
    path('aboutus/', aboutus, name='aboutus'),
    path('register/', register, name='register'),
    path('login/', loginpage, name='login'),
    path('logout/', logoutUser, name='logout'),
    path('mytrips/', mytrips, name='mytrips'),
    path('booking/', book, name='booking'),
    path('bookingf/', bookingfl, name='flight'),
    path('packages/<str:card_title>/<str:card_text>/<str:city>/', packages, name='packages'),
    path('bookform/<str:card_title>/<str:card_text>/<str:city>/', bookform, name='bookform'),
    path('payment_success/', payment_success, name='payment_success'),
    path('final/', final_view, name='final'),
    path('order_success/', TemplateView.as_view(template_name="order_success.html"), name='order_success'),
    path('pdf/', pdf, name='pdf'),
]
