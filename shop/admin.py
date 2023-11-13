from django.contrib import admin

from .models import User, Purchase, Refund, Product

admin.site.register(User)
admin.site.register(Purchase)
admin.site.register(Refund)
admin.site.register(Product)


