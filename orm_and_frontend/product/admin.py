from django.contrib import admin
from product.models import Product,CartTable

# # Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','price','details','category','is_active','rating','image']
    
admin.site.register(Product,ProductAdmin)
admin.site.register(CartTable)