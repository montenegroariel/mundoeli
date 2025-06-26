from django.db import models
from mundoeli.products.models import Product

class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.total} items"

class SalePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('mercadopago', 'Mercadopago'),
        ('efectivo', 'Efectivo'),
    ]

    sale = models.ForeignKey('Sale', related_name='payments', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_payment_method_display()} - ${self.amount} (Venta #{self.sale.id})"

class SaleDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x ${self.price} = ${self.quantity * self.price}"

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"