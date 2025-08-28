from django.contrib import admin
from .models import Product

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "barcode", "price", "stock", "active")
    list_filter = ("active", "stock")
    search_fields = ("name", "barcode", "description")
    readonly_fields = ("created_at", "updated_at")


# admin.py
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        'action_time',
        'user_link',
        'content_type',
        'object_link',
        'action_flag_display',
        'change_message_display'
    ]
    list_filter = [
        'action_flag',
        'action_time',
        'content_type',
    ]
    search_fields = [
        'object_repr',
        'change_message',
        'user__username',
        'user__first_name',
        'user__last_name',
    ]
    date_hierarchy = 'action_time'
    readonly_fields = [
        'action_time',
        'user',
        'content_type',
        'object_id',
        'object_repr',
        'action_flag',
        'change_message'
    ]
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def user_link(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'Usuario'
    user_link.admin_order_field = 'user__username'

    def object_link(self, obj):
        if obj.content_type and obj.object_id:
            try:
                url = reverse(
                    f'admin:{obj.content_type.app_label}_{obj.content_type.model}_change',
                    args=[obj.object_id]
                )
                return format_html('<a href="{}">{}</a>', url, obj.object_repr)
            except:
                return obj.object_repr
        return obj.object_repr
    object_link.short_description = 'Objeto'
    object_link.admin_order_field = 'object_repr'

    def action_flag_display(self, obj):
        flags = {
            ADDITION: format_html('<span style="color: green;">➕ Creado</span>'),
            CHANGE: format_html('<span style="color: orange;">✏️ Modificado</span>'),
            DELETION: format_html('<span style="color: red;">🗑️ Eliminado</span>'),
        }
        return flags.get(obj.action_flag, obj.action_flag)
    action_flag_display.short_description = 'Acción'
    action_flag_display.admin_order_field = 'action_flag'

    def change_message_display(self, obj):
        if obj.change_message:
            # Limitar la longitud del mensaje para mejor visualización
            message = obj.change_message
            if len(message) > 100:
                message = message[:100] + '...'
            return format_html('<span title="{}">{}</span>', obj.change_message, message)
        return '-'
    change_message_display.short_description = 'Mensaje de cambio'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')

# Registrar el modelo
admin.site.register(LogEntry, LogEntryAdmin)