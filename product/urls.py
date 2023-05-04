from django.urls import path
from .views import ProductListAPIView, ProductCreateAPIView, ProductDetailAPIView, CategoryCreateAPIView, \
    CategoryListAPIView, CategoryDeleteAPIView, CategoryUpdateAPIView, ProductDeleteAPIView, ProductUpdateAPIView, \
    ProductFilter, PaymentAPIView, CommentCreateAPIView
from .models import Product
from django_filters.views import FilterView

urlpatterns = [
    path('list/', ProductListAPIView.as_view(), name='product-list'),
    path('list/category', CategoryListAPIView.as_view(), name='category-list'),
    path('create/', ProductCreateAPIView.as_view(), name='product-create'),
    path('create/category', CategoryCreateAPIView.as_view(), name='category-create'),
    path('<int:id>/delete/category', CategoryDeleteAPIView.as_view(), name='category-delete'),
    path('<int:id>/delete/', ProductDeleteAPIView.as_view(), name='product-delete'),
    path('<int:id>/update/category', CategoryUpdateAPIView.as_view(), name='category-delete'),
    path('<int:id>/update/', ProductUpdateAPIView.as_view(), name='product-delete'),
    path('<int:id>/comment/', CommentCreateAPIView.as_view(), name='product-comment'),
    path('<int:id>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('list/', FilterView.as_view(filterset_class=ProductFilter, queryset=Product.objects.all()), name='product-list'),
    path('payment/<int:id>/', PaymentAPIView.as_view(), name='create-checkout-session')
]
