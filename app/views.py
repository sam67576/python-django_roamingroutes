from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import OrderForm, CreateUserForm
from .models import Order
from django.views.generic.base import TemplateView
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
import traceback


def first(request):
    return render(request, "first.html")

def index(request):
    return render(request, "index.html")

def aboutus(request):
    return render(request, "aboutus.html")

@login_required(login_url='login')
def book(request):
    return render(request, "booking.html")

@login_required(login_url='login')
def mytrips(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-arrival_date')
    context = {'orders': user_orders}
    return render(request, "mytrips.html", context)

class MyCustomView(TemplateView):
    template_name = 'your_template_name.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_url'] = '/admin/'
        return context

def bookingfl(request):
    card_title = request.GET.get('card_title')
    card_text = request.GET.get('card_text')
    city = request.GET.get('city')
    source = request.GET.get('source')

    if source == 'book':
        return redirect('packages', card_title=card_title, card_text=card_text, city=city)
    elif source == 'packages':
        return redirect('bookform', card_title=card_title, card_text=card_text, city=city)
    else:
        return redirect('home')

def packages(request, card_title=None, card_text=None, city=None):
    context = {'card_title': card_title, 'card_text': card_text, 'city': city}
    return render(request, "packages.html", context)


logger = logging.getLogger(__name__)
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

@login_required(login_url='login')
def bookform(request, card_title=None, card_text=None, city=None):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user

            # Process additional passengers if any
            additional_passengers_count = int(request.POST.get('additional_passengers_count', 0))
            additional_passengers = []
            for i in range(additional_passengers_count):
                passenger_name = request.POST.get(f'form-{i}-first_name')
                passenger_age = request.POST.get(f'form-{i}-age')
                if passenger_name and passenger_age:
                    additional_passengers.append({
                        'name': passenger_name,
                        'age': passenger_age
                    })

            order.additional_passengers = additional_passengers
            order.save()

            # Store order ID in session
            request.session['order_id'] = order.id
            logger.debug(f"Order ID {order.id} saved in session.")

            # Redirect to final_view for payment
            return redirect('final_view')

        else:
            messages.error(request, 'Form is invalid.')

    else:
        form = OrderForm()

    context = {
        'form': form,
        'card_title': card_title,
        'card_text': card_text,
        'city': city,
    }
    return render(request, "bookform.html", context)




razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

logger = logging.getLogger(__name__)





@csrf_exempt
@login_required(login_url='login')
def final_view(request):
    if request.method == 'POST':
        logger.debug("POST request received in final_view")
        logger.debug("Form data: %s", request.POST)
        
        try:
            # Extract and log form data
            passenger_name = request.POST.get('passenger_name')
            passenger_age = request.POST.get('passenger_age')
            phone_number = request.POST.get('phone_number')
            hotel_name = request.POST.get('hotel_name')
            arrival_date = request.POST.get('arrival_date')
            departure_date = request.POST.get('departure_date')
            rooms = request.POST.get('rooms')
            adults = request.POST.get('adults')
            children = request.POST.get('children')
            flying_from = request.POST.get('flying_from')
            flying_to = request.POST.get('flying_to')
            airline = request.POST.get('airline')
            travel_class = request.POST.get('travel_class')

            user = request.user  # Get the current logged-in user

            # Save main passenger order
            order = Order(
                user=user,
                passenger_name=passenger_name,
                passenger_age=passenger_age,
                phone_number=phone_number,
                hotel_name=hotel_name,
                arrival_date=arrival_date,
                departure_date=departure_date,
                rooms=rooms,
                adults=adults,
                children=children,
                flying_from=flying_from,
                flying_to=flying_to,
                airline=airline,
                travel_class=travel_class
            )
            order.save()
            logger.debug("Main passenger order saved: %s", order)

            # Process additional passengers
            additional_passengers_count = int(request.POST.get('additional_passengers_count', 0))
            for i in range(1, additional_passengers_count + 1):
                additional_passenger_name = request.POST.get(f'form-{i}-first_name')
                additional_passenger_age = request.POST.get(f'form-{i}-age')
                
                additional_order = Order(
                    user=user,
                    passenger_name=additional_passenger_name,
                    passenger_age=additional_passenger_age,
                    phone_number=phone_number,
                    hotel_name=hotel_name,
                    arrival_date=arrival_date,
                    departure_date=departure_date,
                    rooms=rooms,
                    adults=adults,
                    children=children,
                    flying_from=flying_from,
                    flying_to=flying_to,
                    airline=airline,
                    travel_class=travel_class
                )
                additional_order.save()
                logger.debug("Additional passenger order saved: %s", additional_order)
            
            # Create a Razorpay order
            amount = 100000  # Amount in paise (1000 paise = 10 INR)
            currency = "INR"
            razorpay_order = razorpay_client.order.create({
                "amount": amount,
                "currency": currency,
                "payment_capture": "1"
            })
            logger.debug("Razorpay order created: %s", razorpay_order)

            # Save the Razorpay order ID and order details in the session
            request.session['razorpay_order_id'] = razorpay_order['id']
            request.session['order_id'] = order.id

            context = {
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_merchant_key': settings.RAZORPAY_API_KEY,
                'amount': amount,
                'currency': currency,
            }

            return render(request, 'payment.html', context)
        
        except Exception as e:
            logger.error("Error saving order: %s", e)
            return render(request, 'final.html', {'message': 'Booking failed. Please try again.'})
    
    return render(request, 'final.html', {'message': 'Booking failed. Please try again.'})







@csrf_exempt
@login_required(login_url='login')
def payment_success(request):
    if request.method == 'POST':
        try:
            # Get the payment details from the request
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            logger.debug("Payment details received: payment_id=%s, razorpay_order_id=%s, signature=%s", payment_id, razorpay_order_id, signature)

            # Verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            result = razorpay_client.utility.verify_payment_signature(params_dict)
            logger.debug("Payment signature verification result: %s", result)
            
            if result:
                # Payment successful, confirm the order
                order_id = request.session.get('order_id')
                if order_id:
                    order = Order.objects.get(id=order_id)
                    order.payment_status = 'Success'
                    order.save()
                    logger.debug("Order payment status updated: %s", order)
                    return render(request, 'payment_success.html', {'order': order, 'message': 'Payment successful!'})
                else:
                    logger.error("Order ID not found in session.")
                    return HttpResponseBadRequest("Invalid order data.")
            else:
                logger.error("Invalid payment signature.")
                return HttpResponseBadRequest("Invalid payment signature.")
        except Exception as e:
            logger.error("Error occurred during payment verification: %s", e)
            return HttpResponseBadRequest(f"Error occurred: {str(e)}")

    return HttpResponseBadRequest("Invalid request.")









def pdf(request):
    return render(request, "pdf.html")

def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user)
            return redirect('login')
    context = {'form': form}
    return render(request, "register.html", context)

def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

def logoutUser(request):
    logout(request)
    return redirect('login')
