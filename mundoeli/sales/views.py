from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
import json
from .models import Sale, SaleDetail, Product, SalePayment, OrderDraft
from django.contrib.auth.decorators import login_required

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


from django.http import HttpResponse

from .api_utils import api_login_required

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def guardar_borrador_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            productos = data.get('productos', [])
            pagos = data.get('pagos', [])
            # Guardar como JSON
            draft = OrderDraft.objects.create(
                user=request.user,
                products=productos,
                payments=pagos,
            )
            return JsonResponse({'status': 'ok', 'draft_id': draft.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def cargar_borrador_orden(request, draft_id):
    draft = get_object_or_404(OrderDraft, id=draft_id, user=request.user, is_active=True)
    # Marcar como inactivo al cargar
    draft.is_active = False
    draft.save(update_fields=["is_active"])
    return JsonResponse({
        'id': draft.id,
        'products': draft.products,
        'payments': draft.payments,
        'created_at': draft.created_at.strftime('%Y-%m-%d %H:%M'),
        'updated_at': draft.updated_at.strftime('%Y-%m-%d %H:%M'),
    })

@login_required
def listar_borradores_orden(request):
    drafts = OrderDraft.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
    # Para API
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('api'):
        draft_list = [
            {
                'id': d.id,
                'created_at': d.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': d.updated_at.strftime('%Y-%m-%d %H:%M'),
                'products': d.products,
                'payments': d.payments,
            } for d in drafts
        ]
        return JsonResponse({'drafts': draft_list})
    # Para vista HTML
    return render(request, 'sales/order_drafts.html', {'drafts': drafts})

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

