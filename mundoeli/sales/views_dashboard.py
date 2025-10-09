from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate
from .models import Sale, SalePayment
import json
from datetime import timedelta, date

from django.contrib.auth.decorators import login_required

@login_required
def sales_dashboard(request):
    from .models import SaleDetail
    import datetime
    # Ventas diarias de los últimos 30 días (para los gráficos)
    today = date.today()
    thirty_days_ago = today - timedelta(days=29)
    sales_by_day = (
        Sale.objects.filter(date__date__gte=thirty_days_ago)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Sum('total'))
        .order_by('day')
    )
    days = []
    totals = []
    for entry in sales_by_day:
        days.append(entry['day'].strftime('%d/%m'))
        totals.append(float(entry['total']))

    # Total de ventas por método de pago (para los gráficos)
    payments_summary = (
        SalePayment.objects.values('payment_method')
        .annotate(total=Sum('amount'))
    )
    payment_labels = []
    payment_totals = []
    for entry in payments_summary:
        label = dict(SalePayment.PAYMENT_METHOD_CHOICES).get(entry['payment_method'], entry['payment_method'])
        payment_labels.append(label)
        payment_totals.append(float(entry['total']))

    # --- Buscador por rango de fechas ---
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    sales_list = []
    total_sales = 0
    payment_summary_day = {}
    total_profit = 0
    if date_from and date_to:
        try:
            filter_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            filter_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            sales_qs = Sale.objects.filter(date__date__gte=filter_from, date__date__lte=filter_to).order_by('-date')
            product_id = request.GET.get('product_id')
            if product_id:
                sales_qs = sales_qs.filter(saledetail__product_id=product_id)
            for sale in sales_qs:
                details = SaleDetail.objects.filter(sale=sale)
                if product_id:
                    details = details.filter(product_id=product_id)
                sale_payments = sale.payments.all()
                sales_list.append({
                    'id': sale.id,
                    'date': sale.date,
                    'total': sum([float(d.price) * d.quantity for d in details]),
                    'details': details,
                    'payments': sale_payments,
                })
                total_sales += sum([float(d.price) * d.quantity for d in details])
                # Calcular ganancia por cada detalle
                for d in details:
                    if d.product.cost is not None:
                        total_profit += (float(d.price) - float(d.product.cost)) * d.quantity
                # Sumar totales por método de pago
                if product_id:
                    # Prorratear el pago según el subtotal del producto respecto al total de la venta
                    subtotal_producto = sum([float(d.price) * d.quantity for d in details])
                    if sale.total and subtotal_producto:
                        proporcion = subtotal_producto / float(sale.total)
                        for pay in sale_payments:
                            label = dict(SalePayment.PAYMENT_METHOD_CHOICES).get(pay.payment_method, pay.payment_method)
                            payment_summary_day[label] = payment_summary_day.get(label, 0) + float(pay.amount) * proporcion
                else:
                    for pay in sale_payments:
                        label = dict(SalePayment.PAYMENT_METHOD_CHOICES).get(pay.payment_method, pay.payment_method)
                        payment_summary_day[label] = payment_summary_day.get(label, 0) + float(pay.amount)
            # Top/Bottom 10 productos por cantidad vendida en el rango
            product_sales_qs = (
                SaleDetail.objects
                .filter(sale__date__date__gte=filter_from, sale__date__date__lte=filter_to)
                .values('product__id', 'product__name')
                .annotate(total_qty=Sum('quantity'))
            )
            top_products = list(product_sales_qs.order_by('-total_qty')[:10])
            bottom_products = list(product_sales_qs.order_by('total_qty')[:10])
        except Exception as e:
            sales_list = []
            total_sales = 0
            payment_summary_day = {}
            top_products = []
            bottom_products = []
    from mundoeli.products.models import Product
    products = Product.objects.filter(active=True).order_by('name')
    context = {
        'days': json.dumps(days),
        'totals': json.dumps(totals),
        'payment_labels': json.dumps(payment_labels),
        'payment_totals': json.dumps(payment_totals),
        # Para el buscador:
        'sales_list': sales_list,
        'date_from': date_from,
        'date_to': date_to,
        'total_sales': total_sales,
        'payment_summary_day': payment_summary_day,
        'total_profit': total_profit,
        'products': products,
        'top_products': top_products if date_from and date_to else [],
        'bottom_products': bottom_products if date_from and date_to else [],
    }
    return render(request, 'pages/sales.html', context)
