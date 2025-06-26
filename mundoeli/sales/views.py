from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Sale, SaleDetail, Product

@csrf_exempt
def save_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = data.get('total')
            productos = data.get('productos', [])

            # Crear la venta
            sale = Sale.objects.create(total=total)

            # Crear los detalles de venta
            for p in productos:
                product = Product.objects.get(id=p['id'])
                SaleDetail.objects.create(
                    sale=sale,
                    product=product,
                    quantity=p['quantity'],
                    price=p['price']
                )
            return JsonResponse({'status': 'ok', 'sale_id': sale.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

