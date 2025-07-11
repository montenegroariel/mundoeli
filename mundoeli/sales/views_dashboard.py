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
    if date_from and date_to:
        try:
            filter_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            filter_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            sales = Sale.objects.filter(date__date__gte=filter_from, date__date__lte=filter_to).order_by('-date')
            for sale in sales:
                details = SaleDetail.objects.filter(sale=sale)
                sale_payments = sale.payments.all()
                sales_list.append({
                    'id': sale.id,
                    'date': sale.date,
                    'total': sale.total,
                    'details': details,
                    'payments': sale_payments,
                })
                total_sales += float(sale.total)
                # Sumar totales por método de pago
                for pay in sale_payments:
                    label = dict(SalePayment.PAYMENT_METHOD_CHOICES).get(pay.payment_method, pay.payment_method)
                    payment_summary_day[label] = payment_summary_day.get(label, 0) + float(pay.amount)
        except Exception as e:
            sales_list = []
            total_sales = 0
            payment_summary_day = {}
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
    }
    return render(request, 'pages/sales.html', context)
