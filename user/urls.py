from django.urls import path
from .views import LoginView, VendorRegisterView, CustomerRegisterView, VendorListView, CustomerProfileView, \
    VendorProfileView, VendorDetailView, CustomerCartView, CustomerListView, AddToCartView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('vendor/register/', VendorRegisterView.as_view(), name='vendor-register'),
    path('customer/register/', CustomerRegisterView.as_view(), name='customer-register'),
    path('vendor/list', VendorListView.as_view(), name='vendor_list'),
    path('customer/list', CustomerListView.as_view(), name='vendor_list'),
    path('customer/<int:id>', CustomerProfileView.as_view(), name='customer-profile'),
    path('customer/cart/<int:id>', CustomerCartView.as_view(), name='customer-cart'),
    path('vendor/<str:token>', VendorProfileView.as_view(), name='vendor-profile'),
    path('vendor/profile/<int:id>', VendorDetailView.as_view(), name='vendor-detail'),
    path('customer/create/cart/', AddToCartView.as_view(), name='customer-cart'),
]
