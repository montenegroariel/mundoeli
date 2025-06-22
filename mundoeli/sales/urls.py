from django.urls import path
from . import views

urlpatterns = [
    path('api/save-sale/', views.save_sale, name='save_sale'),
]
