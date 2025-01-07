from django.contrib import admin
from django.urls import path
from OnlineShopApp import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page and core views
    path('', views.index, name='index'),
    path('about/', views.about_us, name='about_us'),

    # Product-related views
    path('products/<int:myid>/', views.productView, name='productView'),
    
    # Checkout (with optional myid parameter)
    path('products/<int:myid>/checkout/', views.checkout, name='checkout'),
    path('checkout/', views.checkout, name='checkout'),

    # Order and tracking
    path('tracker/', views.tracker, name='tracker'),
    path('orders/', views.orders, name='orders'),

    # Search functionality
    path('search/', views.search, name='search'),

    # Authentication
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='OnlineShopApp/logout.html'), name='logout'),
    path('accounts/profile/', lambda request: redirect('/')),  # Redirect to home after login
    path('register/', views.register, name='register'),

    # Handle unauthenticated access
    path('unauthenticated/', views.login_required_redirect, name='login_required_redirect'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# No need to serve static files manually in `urlpatterns`, Django does it automatically during development.
