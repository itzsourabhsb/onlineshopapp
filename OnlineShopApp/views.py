from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Product, OrderUpdate, Orders
from .forms import RegistrationForm, LoginForm
from math import ceil
import json

# Create your views here.
def about_us(request):
    return render(request, 'OnlineShopApp/about_us.html')

@login_required
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds}
    return render(request, 'OnlineShopApp/index.html', params)

def searchMatch(query, item):
    '''Return true only if query matches the item.'''
    return query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower()

@login_required
def search(request):
    query = request.GET.get('search', '').lower()  # Convert query to lower case
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])

    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query) < 4:
        params['msg'] = "Please make sure to enter a relevant search query."

    return render(request, 'OnlineShopApp/search.html', params)

@login_required
def productView(request, myid):
    product = Product.objects.filter(id=myid).first()  # Use .first() to avoid index error
    return render(request, 'OnlineShopApp/prodView.html', {'product': product})

@login_required
def checkout(request, myid=None):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        
        # Handle cases with or without myid
        if myid:
            product = Product.objects.filter(id=myid).first()  # Optional, if you want to use product data
        else:
            product = None  # Handle as needed if no product is selected
        
        # Process the order
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'OnlineShopApp/checkout.html', {'thank': thank, 'id': id, 'product': product})
    return render(request, 'OnlineShopApp/checkout.html')



@login_required
def tracker(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email).first()  # Use .first() to avoid index error
            if order:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = [{'text': item.update_desc, 'time': item.timestamp} for item in update]

                # Include order details in the response
                order_details = {
                    'order_id': order.order_id,
                    'items_json': order.items_json,
                    'name': order.name,
                    'email': order.email,
                    'address': order.address,
                    'city': order.city,
                    'state': order.state,
                    'zip_code': order.zip_code,
                    'phone': order.phone,
                }

                response = json.dumps({
                    'order_details': order_details,
                    'updates': updates
                }, default=str)

                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception:
            return HttpResponse('{}')

    return render(request, 'OnlineShopApp/tracker.html')


@login_required
def orders(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        try:
            # Fetch orders based on user email
            orders = Orders.objects.filter(email=email)
            if orders.exists():
                orders_list = []
                for order in orders:
                    updates = OrderUpdate.objects.filter(order_id=order.order_id)
                    updates_list = [{'text': item.update_desc, 'time': item.timestamp} for item in updates]
                    orders_list.append({
                        'order_id': order.order_id,
                        'items': updates_list
                    })
                response = json.dumps({'orders': orders_list}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse(json.dumps({'message': 'You haven\'t placed any orders yet.'}))
        except Exception:
            return HttpResponse(json.dumps({'error': 'An error occurred'}))
    return render(request, 'OnlineShopApp/orders.html')


@login_required
def place_order(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        # Handle the order processing logic here
        # You can use the same logic as in your checkout view if appropriate
        thank = True
        return render(request, 'OnlineShopApp/place_order.html', {'thank': thank})
    return render(request, 'OnlineShopApp/place_order.html')


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                # Invalid credentials
                return render(request, 'OnlineShopApp/login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = LoginForm()

    return render(request, 'OnlineShopApp/login.html', {'form': form})



def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirect to home or any other page
    else:
        form = RegistrationForm()

    return render(request, 'OnlineShopApp/register.html', {'form': form})

def login_required_redirect(request):
    messages.info(request, "Please login or register to access this page.")
    return redirect('login')
