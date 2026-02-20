from rest_framework import serializers
from decimal import Decimal
from product.models import Category,Product,Review,ProductImage
from django.contrib.auth import get_user_model


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only = True, help_text='Return the number of products in this category')

    class Meta:
        model = Category
        fields = [
            'id','name','description','product_count'
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ProductImage
        fields = ['id','image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name','description','stock', 'price','price_with_tax','images','category','seller'
        ]
    
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
  
    def calculate_tax(self,product):
        return (product.price * Decimal('1.10')).quantize(Decimal('0.01'))    
    def validate_price(self,price):
        if price < 0:
            raise serializers.ValidationError('Price could not be negative')
        return price
    
    

class SimpleUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name='get_current_user_name')
    class Meta:
        model = get_user_model()
        fields = ['id','name']

    def get_current_user_name(self,obj):
        return obj.get_full_name()



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(method_name='get_user')
    class Meta:
        model = Review
        fields = ['id','user','comment','ratings','product']
        read_only_fields = ['user','product',]

    def get_user(self, obj):
        return SimpleUserSerializer(obj.user).data


    def create(self,validated_data):
        product_id = self.context['product_id']
        review = Review.objects.create(product_id = product_id, **validated_data)
        return review
    