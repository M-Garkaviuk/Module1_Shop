from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from shop.models import User, Product, Purchase


class CustomerForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


class PurchaseCreationForm(ModelForm):
    class Meta:
        model = Purchase
        fields = ('product_quantity',)




