from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from shop.models import User, Product


class CustomerForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"




