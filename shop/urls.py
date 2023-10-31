
from django.urls import path
from shop.views import (Login, Logout, Register,
                        ProductListView, ProductCreateView, ProductUpdate)


urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    path('product/create', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/update', ProductUpdate.as_view(), name='product-update'),
    path('registration/', Register.as_view(), name='registration'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

]
