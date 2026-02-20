from django.shortcuts import render
from django.db.models import Prefetch

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,GenericViewSet

from order.models import Cart,CartItem,Order,OrderItem, Wishlist
from order.serializers import CartSerializer,CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, EmptySerializer, WishlistSerializer, SellerOrderSerializer
from order.services import OrderService

# Create your views here.
class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    """
    API endpoint for managing cart in the grocery store
     - Allows authenticated user to create , update, delete cart
     
    """
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items__product').filter(user = self.request.user)
    serializer_class = CartSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class CartItemViewSet(ModelViewSet):
    """
    API endpoint for managing cart items
     - Allows authenticated user to view their cart items in their cart
     - Allows authenticated user to create , update, delete cartitems from their cart
    """
    # queryset = CartItem.objects.all()
    # serializer_class = CartItemSerializer 
    http_method_names=['get','post','patch','delete']
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self,'swagger_fake_view', False):
            return context
        return {'cart_id': self.kwargs['cart_pk']}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        # return CartItem.objects.select_related('product').filter(cart_id = self.kwargs['cart_pk'])
        return CartItem.objects.select_related('product').filter(cart_id = self.kwargs.get('cart_pk'))
    

class OrderViewSet(ModelViewSet):
    """
    API endpoint for managing orders
     - Allows authenticated user to create , update, cancel orders
     - Allows authenticated user to view their purchase history
    """
    http_method_names = ['get','post','patch','delete','head','options']
    
    @action(detail=True, methods=['post'])
    def cancel(self,request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order=order, user=request.user)
        return Response({'status':'order cancled'})
    
    @action(detail=True,methods=['patch'])
    def update_status(self,request,pk=None):
        order = self.get_object()
        serializer = UpdateOrderSerializer(order,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f"status updated successfully to {request.data['status']}"})
    
    @action(detail=False, methods=['get'], url_path='my-purchase-history')
    def purchase_history(self, request):
        orders = Order.objects.prefetch_related('items__product').filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ['update_status','destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user= self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptySerializer
        # if self.request.method == 'POST':
        #     return CreateOrderSerializer
        if self.action == 'create':
            return CreateOrderSerializer
        # elif self.request.method == 'PATCH':
        #     return UpdateOrderSerializer
        elif self.action == 'update_status':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_serializer_context()
        return {'user_id': self.request.user.id, 'user':self.request.user}
    



class WishlistViewSet(ModelViewSet):
    '''
    To add in wishlish
    method: POST 
    endpoint: /api/v1/wishlist/
    value for example:
    {
        "product_id": 5
    }
    '''
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def get_serializer_context(self):
        return {'request': self.request}
    


class SellerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard for sellers:
    - List orders that include products created by the logged-in seller
    - Read-only: cannot edit orders
    """
    serializer_class = SellerOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'seller' and not user.is_staff:
            return Order.objects.none()  

        seller_items = OrderItem.objects.filter(product__seller=user)
        return Order.objects.prefetch_related(
            Prefetch('items', queryset=seller_items, to_attr='seller_items')
        ).filter(items__product__seller=user).distinct()