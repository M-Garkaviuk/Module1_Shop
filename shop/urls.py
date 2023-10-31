
from django.urls import path
from shop.views import (Login, Logout, Register,
                        ProductListView, ProductCreateView, ProductUpdate, ProductPurchaseView,
                        UserCabinetView, RefundRequestView)


urlpatterns = [
    path('', ProductListView.as_view(), name='index'),
    path('product/create', ProductCreateView.as_view(), name='product-create'),
    path('product/purchase', ProductPurchaseView.as_view(), name='product-purchase'),
    path('cabinet/', UserCabinetView.as_view(), name='user-cabinet'),
    path('cabinet/<int:pk>/refund', RefundRequestView.as_view(), name='refund-request'),
    path('product/<int:pk>/update', ProductUpdate.as_view(), name='product-update'),
    path('registration/', Register.as_view(), name='registration'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

]
