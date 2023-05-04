from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import Http404
import jwt
from market.settings import SECRET_KEY
from rest_framework_simplejwt import exceptions
from product.models import Product, Cart, Purchase
from product.serializers import ProductSerializer, CartSerializer, PurchaseSerializer

from .models import Vendor, Customer
from .permissions import AnonPermissionOnly
from .serializers import MyTokenObtainPairSerializer, VendorRegisterSerializer, CustomerRegisterSerializer, \
    VendorProfileSerializer


def decode_auth_token(token):
    try:
        user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        msg = 'Signature has expired, Login again'
        raise exceptions.AuthenticationFailed(msg)
    except jwt.DecodeError:
        msg = 'Error decoding signature, type valid token'
        raise exceptions.AuthenticationFailed(msg)
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed()
    return user


class LoginView(TokenObtainPairView):
    permission_classes = (AnonPermissionOnly,)
    serializer_class = MyTokenObtainPairSerializer


class VendorRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VendorRegisterSerializer(data=request.data)
        if serializer.is_valid():
            vendor = Vendor.objects.create(
                email=request.data['email'],
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
                description=request.data['description'],
                is_Vendor=True
            )
            vendor.set_password(request.data['password'])
            vendor.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CustomerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            customer = Customer.objects.create(
                email=request.data['email'],
                name=request.data['name'],
                second_name=request.data['second_name'],
                phone_number=request.data['phone_number'],
                card_number=request.data['card_number'],
                address=request.data['address'],
                post_code=request.data['post_code'],
                is_Vendor=False
            )
            customer.set_password(request.data['password'])
            customer.save()
            cart = Cart.objects.create(
                customer=customer
            )
            cart.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        vendors = Vendor.objects.all()
        serializer = VendorRegisterSerializer(vendors, many=True)
        count = vendors.count()
        data = {
            "count": count,
            "vendors": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomerListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        vendors = Customer.objects.all()
        serializer = CustomerRegisterSerializer(vendors, many=True)
        count = vendors.count()
        data = {
            "count": count,
            "customers": serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomerProfileView(APIView):

    def get_object(self, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            raise Http404

    def get(self, request, id):
        customer = self.get_object(id)
        serializer = CustomerRegisterSerializer(customer)
        purchases = Purchase.objects.filter(customer=customer)
        serializer2 = PurchaseSerializer(purchases, many=True)
        data = {
            "customer": serializer.data,
            "purchases": serializer2.data
        }
        return Response(data, status=status.HTTP_200_OK)


class VendorProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, token):
        try:
            user = decode_auth_token(token)
            return Vendor.objects.get(id=user['user_id'])
        except Vendor.DoesNotExist:
            raise Http404

    def get(self, request, token):
        vendor = self.get_object(token)
        serializer_vendor = VendorProfileSerializer(vendor)
        product = Product.objects.filter(vendor=vendor)
        serializer_product = ProductSerializer(product, many=True)
        data = {
            "vendor": serializer_vendor.data,
            "product": serializer_product.data
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, token):
        snippet = self.get_object(token)
        serializer = VendorProfileSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, token):
        snippet = self.get_object(token)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, id):
        try:
            return Vendor.objects.get(id=id)
        except Vendor.DoesNotExist:
            raise Http404

    def get(self, request, id):
        vendor = self.get_object(id)
        serializer_vendor = VendorRegisterSerializer(vendor)
        product = Product.objects.filter(vendor=vendor)
        serializer_product = ProductSerializer(product, many=True)
        data = {
             "vendor": serializer_vendor.data,
             "product": serializer_product.data
        }
        return Response(data, status=status.HTTP_200_OK)


class CustomerCartView(APIView):

    def get_object(self, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            raise Http404

    # def get(self, request, id):
    #     cart = self.get_object(id)
    #     serializer = CartSerializer
    #     prod_serializer = ProductSerializer(cart.product.all(), many=True)
    #     data = serializer.data
    #     data['products'] = prod_serializer.data
    #     return Response(data, status=status.HTTP_200_OK)

    def get(self, request, id):
        customer = self.get_object(id)
        serializer_customer = CustomerRegisterSerializer(customer)
        # cart = Cart.objects.filter(customer=customer)
        # serializer_cart = CartSerializer(cart, many=True)
        product = Product.objects.filter(cart__customer=customer)
        serializer_product = ProductSerializer(product, many=True)
        data = {
             "customer": serializer_customer.data,
             # "cart": serializer_cart.data,
             "cart": serializer_product.data
        }
        return Response(data, status=status.HTTP_200_OK)


class AddToCartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, user_id):
        try:
            return Cart.objects.get(customer_id=user_id)
        except Cart.DoesNotExist:
            raise Http404

    def put(self, request, user_id):
        cart = self.get_object(user_id)
        serializer = CartSerializer(cart, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







