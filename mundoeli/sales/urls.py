from django.urls import path
from django.views.generic import TemplateView
from . import views
from . import views_dashboard

urlpatterns = [
    path('sales/', views_dashboard.sales_dashboard, name='sales'),
    path('api/save-sale/', views.save_sale, name='save_sale'),
]
