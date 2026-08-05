from django.contrib import admin
from .models import UserProfile, Category, Size, Color, Product, ProductImage, Sale


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent']
    list_filter = ['parent']


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'base_price', 'selling_price', 'stock', 'is_low_stock', 'is_out_of_stock']
    list_filter = ['category']
    search_fields = ['name', 'fabric']
    inlines = [ProductImageInline]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['product_name_snapshot', 'quantity', 'selling_price_snapshot', 'total_profit', 'payment_method', 'timestamp']
    list_filter = ['payment_method', 'timestamp']
    search_fields = ['product_name_snapshot', 'customer_name']