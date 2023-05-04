from rest_framework import serializers
from .models import Product, Category, Cart, Comment, Purchase
from django.db.models import Max, Avg, Min


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["name"]


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["comment", "customer"]


class PurchaseSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Purchase
        fields = '__all__'

