from django.contrib import admin
from .models import Sale

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("date", "total")
    list_filter = ("date", "total")
    search_fields = ("date", "total")
    readonly_fields = ("date", "total")