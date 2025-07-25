from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
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

            if not productos:
                return JsonResponse({'error': 'Debe agregar al menos un producto para registrar la venta.'}, status=400)

            # Crear la venta
            sale = Sale.objects.create(total=total)

            # Crear los detalles de venta y descontar stock
            for p in productos:
                product = Product.objects.get(id=p['id'])
                cantidad = p['quantity']
                #if product.stock < cantidad:
                #    raise Exception(f'Stock insuficiente para el producto {product.name}')
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


def sales_list(request):
    sales = Sale.objects.all().order_by('-date')
    return render(request, 'pages/sales_list.html', {'sales': sales})


def reprint_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    details = SaleDetail.objects.filter(sale=sale)
    payments = sale.payments.all()
    # Convertir a lista serializable para impresión Bluetooth
    details_list = [
        {
            "product_name": d.product.name,
            "price": str(d.price),
            "quantity": d.quantity
        }
        for d in details
    ]
    return render(request, 'pages/receipt.html', {
        'sale': sale,
        'details': details,
        'payments': payments,
        'details_list': details_list,
    })

