from django.db import models
from django.core.cache import cache
from django.utils.text import slugify

class Category(models.Model):
    """Category model for products"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Invalidate category cache when saving
        cache.delete('category_list')
        cache.delete(f'category_{self.id}')
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Invalidate category cache when deleting
        cache.delete('category_list')
        cache.delete(f'category_{self.id}')
        
        super().delete(*args, **kwargs)

class Product(models.Model):
    """Product model for the e-commerce store"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Invalidate product cache when saving
        cache.delete('product_list')
        cache.delete(f'product_{self.id}')
        cache.delete(f'products_category_{self.category_id}')
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Invalidate product cache when deleting
        cache.delete('product_list')
        cache.delete(f'product_{self.id}')
        cache.delete(f'products_category_{self.category_id}')
        
        super().delete(*args, **kwargs)