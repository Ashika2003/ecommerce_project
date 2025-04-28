from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), 
        write_only=True,
        source='product'
    )
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True,
       
    )
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']
    
    def validate(self, attrs):
        """Validate that product has enough stock"""
        cart = self.context['cart']
        product = attrs['product']
        quantity = attrs.get('quantity', 1)
        
        # For updates, add current quantity
        instance = self.instance
        if instance and instance.product == product:
            quantity += instance.quantity
            
        if product.stock < quantity:
            raise serializers.ValidationError(f"Not enough stock available. Only {product.stock} remaining.")
        
        return attrs

class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price', 'total_price']
        read_only_fields = ['price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'status', 'shipping_address', 
                 'phone', 'created_at', 'updated_at']
        read_only_fields = ['user', 'total_price', 'created_at', 'updated_at']

class CreateOrderSerializer(serializers.ModelSerializer):
    """Serializer for creating a new order"""
    class Meta:
        model = Order
        fields = ['shipping_address', 'phone']
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Get the user's cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise serializers.ValidationError("You don't have any items in your cart.")
        
        # Check if cart has items
        if cart.items.count() == 0:
            raise serializers.ValidationError("Your cart is empty.")
        
        # Create the order
        order = Order.objects.create(
            user=user,
            total_price=cart.total_price,
            shipping_address=validated_data['shipping_address'],
            phone=validated_data['phone'],
            status='pending'
        )
        
        # Create order items and update product stock
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            # Update product stock
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()
        
        # Clear the cart
        cart.items.all().delete()
        
        return order

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status"""
    class Meta:
        model = Order
        fields = ['status']