from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Prefetch
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer, 
    CreateOrderSerializer, OrderStatusUpdateSerializer
)

class CartItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing cart items"""
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return items for current user's cart"""
        user = self.request.user
        return CartItem.objects.filter(cart__user=user).select_related('product', 'product__category')
    
    def get_serializer_context(self):
        """Add cart to serializer context"""
        context = super().get_serializer_context()
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        context['cart'] = cart
        return context
    
    def create(self, request, *args, **kwargs):
        """Add item to cart or update quantity if it exists"""
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        try:
            # Try to get existing cart item
            if CartItem.objects.get(cart=cart, product_id=product_id):
              cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            print("cart_item:",cart_item)
            # Update quantity
            cart_item.quantity += quantity
            serializer = self.get_serializer(cart_item, data={
                'product_id': product_id,
                'quantity': cart_item.quantity
            }, partial=True)
            
        except CartItem.DoesNotExist:
            # Create new cart item
            serializer = self.get_serializer(data={
                'product_id': product_id,
                'quantity': quantity
            })
        
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        """Save cart item with cart from context"""
        user = self.request.user
        cart, created = Cart.objects.get_or_create(user=user)
        serializer.save(cart=cart)


class CartView(viewsets.ModelViewSet):  # Use ModelViewSet for default actions
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Override this to filter carts by user"""
        return Cart.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Get cart for the current user"""
        cart = self.get_object()  # This will get the cart for the current user
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
            cart.items.all().delete()
            return Response({"message": "Cart cleared successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response({"message": "Cart is already empty"}, status=status.HTTP_204_NO_CONTENT)
        
class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return orders for current user"""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related(
                Prefetch('items', queryset=OrderItem.objects.select_related('product'))
            )
        return Order.objects.filter(user=user).prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return CreateOrderSerializer
        elif self.action == 'update_status' and self.request.user.is_staff:
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        """Create order for current user"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        """Update order status (admin only)"""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)