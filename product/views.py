from django.shortcuts import render
from django.views import View
from user.models import Customer
from django.conf import settings
from rest_framework.generics import ListAPIView
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Product, Category, Cart, Comment, Purchase
from .serializers import ProductSerializer, CategorySerializer, CommentSerializer
from user.permissions import IsVendorPermission, IsOwnerOrReadOnly
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg, Min, Max
import stripe


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = ('category', 'name')


class ProductListPagination(PageNumberPagination):
    page_size = 2
    page_query_param = 'page_size'


class ProductListAPIView(ListAPIView):
    permission_classes = [permissions.AllowAny]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    pagination_class = ProductListPagination
    page_size = 2
    count = queryset.count()

    def get_queryset(self):
        queryset = super().get_queryset()
        return self.filterset_class(self.request.GET, queryset=queryset).qs

    def get(self, request):
        queryset = self.get_queryset()
        paginator = ProductListPagination()
        pagination = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(pagination, many=True)
        price = queryset.aggregate(Max('price'), Min('price'), Avg('price'))
        data = {
            "products": serializer.data,
            "avg_price": price
        }
        return paginator.get_paginated_response(data)


class CategoryListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        all_category = Category.objects.all()
        serializer = CategorySerializer(all_category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = Product.objects.create(
                vendor_id=request.data['vendor'],
                category_id=request.data['category'],
                name=request.data['name'],
                description=request.data['description'],
                price=request.data['price']
            )
            product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def get_object_customer(self, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            raise Http404

    def post(self, request, id):
        serializer = CommentSerializer(data=request.data)
        customer = self.get_object_customer(id)
        product = self.get_object(id)
        if serializer.is_valid():
            comment = Comment.objects.create(
                comment=request.data['comment'],
                product=product,
                customer=customer
            )
            comment.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class CommentCreateAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, id):
#         serializer = CommentSerializer(data=request.data)
#         if serializer.is_valid():
#             comment = Comment.objects.create(
#                 comment=request.data['comment'],
#             )
#             comment.customer = request.user.customer
#             comment.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = Category.objects.create(
                name=request.data['name'],
            )
            category.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDeleteAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def delete(self, request, id):
        product = self.get_object(id)
        serializer = ProductSerializer(product)
        product.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class CategoryDeleteAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, id):
        try:
            return Category.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def delete(self, request, id):
        category = self.get_object(id)
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class ProductUpdateAPIView(APIView):
    permission_classes = [IsVendorPermission, IsOwnerOrReadOnly]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def put(self, request, id):
        snippet = self.get_object(id)
        serializer = ProductSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryUpdateAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, id):
        try:
            return Category.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def put(self, request, id):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = self.get_object(id)
            category = Category.objects.update(
                name=request.data['name'],
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):

    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, id):
        product_id = request.data.get('id')
        product = self.get_object(id)
        comments = Comment.objects.filter(product_id=id)
        serializer = ProductSerializer(product)
        serializer2 = CommentSerializer(comments, many=True)
        data = {
            "product": serializer.data,
            "comments": serializer2.data
        }
        return Response(data, status=status.HTTP_200_OK)


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            raise Http404

    def get_object_customer(self, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            raise Http404

    def post(self, request, id):
        # try:
            amount = int(request.data['amount'])
            product = self.get_object(id)
            customer = self.get_object_customer(id)
            card_number = request.data['card_number']
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                payment_method_types=['card'],
                metadata={'integration_check': 'accept_a_payment',
                          'product_name': product.name,
                          'product_description': product.description,
                          'card_number': card_number
                          },
            )

            customer = customer
            purchase = Purchase.objects.create(customer=customer, product=product)
            purchase.save()
            data = {
                    'client_secret': payment_intent.client_secret
            }
            return Response(data, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({
        #         'error': str(e)
        #     }, status=status.HTTP_400_BAD_REQUEST)


