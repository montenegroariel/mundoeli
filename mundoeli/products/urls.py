from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('search-by-barcode/', views.search_by_barcode, name='search_by_barcode'),
    path('api/search-by-barcode/', views.api_search_by_barcode, name='api_search_by_barcode'),
    path('api/search-by-name/', views.api_search_by_name, name='api_search_by_name'),
    path('api/update-stock/', views.update_stock, name='update_stock'),
]