from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "barcode", "price", "stock", "active")
    list_filter = ("active", "stock")
    search_fields = ("name", "barcode", "description")
    readonly_fields = ("created_at", "updated_at")