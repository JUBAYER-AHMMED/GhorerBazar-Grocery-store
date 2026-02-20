from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.db.models import Count
from rest_framework.response import Response
from product.models import Product, Category,Review, ProductImage
from rest_framework import status
from product.serializers import ProductSerializer, CategorySerializer, ReviewSerializer, ProductImageSerializer
from rest_framework.views import APIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend 
from product.filters import ProductFilter
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAuthenticated

from product.paginations import DefaultPagination
# from product.permissions import IsSellerOrAdmin
# from rest_framework.permissions import IsAdminUser , AllowAny
from api.permissions import IsAdminOrReadOnly, FullDjangoModelPermission

from product.permissions import IsReviewAuthorOrReadOnly,IsSellerOrAdminOrReadOnly
from drf_yasg.utils import swagger_auto_schema

from rest_framework import viewsets



class ProductViewSet(ModelViewSet):
    """
    API endpoint for managing products in the e-commerce store
     - Allows authenticated admin to create , update, delete products
     - Allows users to browse ad filter product
     - Support searching by name,description and category
     - Support ordering y price ad updated at
    """

    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['name','description', 'category__name']
    ordering_fields = ['price', 'updated_at']

    permission_classes = [IsSellerOrAdminOrReadOnly]  # <-- updated

    def get_queryset(self):
        return Product.objects.prefetch_related('images').all()

    def perform_create(self, serializer):   # <-- added
        serializer.save(seller=self.request.user)

    @swagger_auto_schema(
        operation_summary='Retrieve a list of products'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a product by seller/admin',
        request_body=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: 'Bad Request'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = ProductImage.objects.filter(product_id = self.kwargs.get('product_pk'))
        return queryset
    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs['product_pk'])

    

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.annotate(product_count = Count('products'))
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Review.objects.filter(product_id = self.kwargs.get('product_pk'))
        return queryset

    def get_serializer_context(self):
        return {'product_id':self.kwargs.get('product_pk')}



class SellerProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard for sellers:
    - List only products created by the logged-in seller
    - Supports filtering, search, and ordering
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']  
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'updated_at']
    pagination_class = DefaultPagination

    def get_queryset(self):
        user = self.request.user
        if user.role == 'seller':
            return Product.objects.filter(seller=user).prefetch_related('images')
        elif user.role == 'admin':
            return Product.objects.all().prefetch_related('images')
        else:
            return Product.objects.none()