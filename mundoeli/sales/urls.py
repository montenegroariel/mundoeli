from django.urls import path
from django.views.generic import TemplateView
from . import views
from . import views_dashboard

urlpatterns = [
    path('sales/', views_dashboard.sales_dashboard, name='sales'),
    path('sales/list/', views.sales_list, name='sales_list'),
    path('sales/reprint/<int:sale_id>/', views.reprint_receipt, name='reprint_receipt'),
    path('api/save-sale/', views.save_sale, name='save_sale'),
    path('api/guardar-borrador-orden/', views.guardar_borrador_orden, name='guardar_borrador_orden'),
    path('api/listar-borradores-orden/', views.listar_borradores_orden, name='listar_borradores_orden'),
    path('api/cargar-borrador-orden/<int:draft_id>/', views.cargar_borrador_orden, name='cargar_borrador_orden'),
]
