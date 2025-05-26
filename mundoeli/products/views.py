from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

from mundoeli.products.models import Product
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
#from .serializers import ProductSerializer


class ProductListView(ListView):
    model = Product
    queryset = Product.objects.filter(active=True)


class ProductCreateView(CreateView):
    model = Product
    fields = ["name", "price", "description", "image"]
    success_url = "/products/"


class ProductDetailView(DetailView):
    model = Product
    queryset = Product.objects.filter(active=True)
    

class ProductUpdateView(UpdateView):
    model = Product
    fields = ["name", "price", "description", "image", "stock"]
    queryset = Product.objects.filter(active=True)


class ProductDeleteView(DeleteView):
    model = Product
    queryset = Product.objects.filter(active=True)
    success_url = "/products/"


def search_by_barcode(request):
    """Vista para mostrar el formulario de búsqueda por código de barras"""
    return render(request, 'products/search_by_barcode.html')

def api_search_by_barcode(request):
    """API endpoint para buscar productos por código de barras"""
    query = request.GET.get('barcode', '').strip()
    
    if not query:
        return JsonResponse({'error': 'Código de barras no proporcionado'}, status=400)
    
    # Primero intentamos buscar por código de barras exacto
    products = list(Product.objects.filter(barcode=query, active=True))
    
    # Si no encontramos nada por código exacto y la consulta parece ser un nombre
    if not products and not query.isdigit():
        # Buscar por nombre
        products = list(Product.objects.filter(
            name__icontains=query,
            active=True
        )[:10])
    
    if not products:
        return JsonResponse({'error': 'No se encontraron productos'}, status=404)
    
    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'barcode': product.barcode,
                'price': str(product.price),
                'stock': product.stock,
                'description': product.description,
                'image_url': product.image.url if product.image else None
            }
            for product in products
        ]
    }
    return JsonResponse(data)

@csrf_exempt
@require_http_methods(["GET"])
def api_search_by_name(request):
    """API endpoint para buscar productos por nombre"""
    try:
        name_query = request.GET.get('name', '').strip()
        
        if not name_query:
            return JsonResponse({'error': 'Debes proporcionar un nombre para buscar'}, status=400)
        
        # Buscar productos que contengan el texto en el nombre (case-insensitive)
        products = Product.objects.filter(
            Q(name__icontains=name_query) & Q(active=True)
        ).order_by('name')[:10]  # Limitamos a 10 resultados
        
        # Formatear los resultados
        products_data = [{
            'id': product.id,
            'name': product.name,
            'barcode': product.barcode,
            'price': float(product.price),
            'stock': product.stock,
            'image': product.image.url if product.image else None
        } for product in products]
        
        return JsonResponse({
            'products': products_data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': 'Error al buscar productos: ' + str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_stock(request):
    try:
        data = json.loads(request.body)
        products = data.get('products', [])
        
        with transaction.atomic():
            for product_data in products:
                product_id = product_data.get('id')
                quantity = product_data.get('quantity', 0)
                
                product = Product.objects.select_for_update().get(id=product_id)
                if product.stock < quantity:
                    raise ValueError(f'Stock insuficiente para el producto {product.name}')
                
                product.stock -= quantity
                product.save()
        
        return JsonResponse({'status': 'success'})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
    except ValueError as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)