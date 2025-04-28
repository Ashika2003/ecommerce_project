from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet, CartView, OrderViewSet

router = DefaultRouter()
router.register('cart-items', CartItemViewSet, basename='cart-item')
router.register('orders', OrderViewSet, basename='order')
router.register('cart', CartView, basename='cart')  

urlpatterns = [
    path('', include(router.urls)),
   
]