from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for the Product model"""
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 
                 'category_name', 'slug', 'image', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']