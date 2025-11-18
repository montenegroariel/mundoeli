from django.contrib import admin
from .models import Product
from import_export import resources  
from import_export.admin import ImportExportMixin


class ProductResource(resources.ModelResource):
    class Meta:
        model = Product
        fields = ('name','cost','description','barcode', 'price', 'stock', 'active', 'id',)


@admin.register(Product)
class ProductAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "barcode", "price", "stock", "active")
    list_filter = ("active", "stock")
    search_fields = ("name", "barcode", "description")
    readonly_fields = ("created_at", "updated_at")

from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_id",
        "object_repr",
        "action_flag",
        "change_message",
    )

    # 🚫 Evitar eliminación de logs
    def has_delete_permission(self, request, obj=None):
        return False
    
    # 🚫 También evitar agregar/editar logs (recomendado)
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    # 🚫 Quitar la acción "eliminar seleccionados"
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions