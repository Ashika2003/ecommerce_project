from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.conf import settings
from django.utils.decorators import method_decorator         
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.db.models import Q
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .filters import ProductFilter
from django.views.decorators.csrf import csrf_exempt
# Cache TTL in seconds
CACHE_TTL = getattr(settings, 'CACHE_TTL', 60 * 60)  # Default 1 hour

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Category instances."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Allow anyone to list and retrieve, but only admin to create, update, delete"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """Override list method to use caching"""
        # Try to get from cache
        cache_key = 'category_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # If not in cache, get from DB
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve method to use caching"""
        instance = self.get_object()
        cache_key = f'category_{instance.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        
        return Response(serializer.data)
    
@method_decorator(csrf_exempt, name='dispatch')   
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Product instances."""
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Allow anyone to list and retrieve, but only admin to create, update, delete"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """Override list to use caching, but skip if filters are applied"""
        # Skip cache if filters are applied
        if len(request.query_params) > 0:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        # Try to get from cache
        cache_key = 'product_list'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # If not in cache, get from DB
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve method to use caching"""
        instance = self.get_object()
        cache_key = f'product_{instance.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, CACHE_TTL)
        
        return Response(serializer.data)