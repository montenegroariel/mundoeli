from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Sale, SaleDetail, Product, SalePayment

@csrf_exempt
def save_sale(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total = data.get('total')
            productos = data.get('productos', [])
            pagos = data.get('pagos', [])

            # Crear la venta
            sale = Sale.objects.create(total=total)

            # Crear los detalles de venta y descontar stock
            for p in productos:
                product = Product.objects.get(id=p['id'])
                cantidad = p['quantity']
                if product.stock < cantidad:
                    raise Exception(f'Stock insuficiente para el producto {product.name}')
                # Descontar stock
                product.stock -= cantidad
                product.save()
                SaleDetail.objects.create(
                    sale=sale,
                    product=product,
                    quantity=cantidad,
                    price=p['price']
                )

            # Crear los pagos asociados
            for pago in pagos:
                SalePayment.objects.create(
                    sale=sale,
                    payment_method=pago['payment_method'],
                    amount=pago['amount']
                )
            return JsonResponse({'status': 'ok', 'sale_id': sale.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

