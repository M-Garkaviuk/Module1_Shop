from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=10000)


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_purchases')
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name='user_products')
    product_quantity = models.PositiveIntegerField()
    purchase_created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product} bought by {self.user} at {self.purchase_created}'

    @property
    def is_refundable(self):
        three_minutes_ago = timezone.now() - timezone.timedelta(minutes=3)
        return self.purchase_created >= three_minutes_ago


class Refund(models.Model):
    refund_time = models.DateTimeField(auto_now_add=True)
    refund_purchase = models.OneToOneField("Purchase", on_delete=models.CASCADE, related_name="refund")

    def __str__(self):
        return f'{self.refund_purchase} return was requested at {self.refund_purchase}'


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.product_name


