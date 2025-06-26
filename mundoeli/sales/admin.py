from django.contrib import admin
from .models import Sale, SaleDetail, SalePayment

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("date", "total")
    list_filter = ("date", "total")
    search_fields = ("date", "total")
    readonly_fields = ("date", "total")

@admin.register(SaleDetail)
class SaleDetailAdmin(admin.ModelAdmin):
    list_display = ("sale", "product", "quantity", "price")
    list_filter = ("sale", "product")
    search_fields = ("sale", "product")

@admin.register(SalePayment)
class SalePaymentAdmin(admin.ModelAdmin):
    list_display = ("sale", "payment_method", "amount")
    list_filter = ("sale", "payment_method")
    search_fields = ("sale", "payment_method")