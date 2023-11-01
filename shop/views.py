from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.views import View
from shop.models import Product, Purchase, Refund
from shop.forms import CustomerForm, ProductForm, PurchaseCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView
from django.db import transaction


class ProductListView(ListView):
    model = Product
    template_name = 'index.html'
    login_url = 'login/'
    extra_context = {'purchase_form': PurchaseCreationForm()}


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = 'new_product.html'
    login_url = 'login/'
    http_method_names = ['get', 'post']
    form_class = ProductForm
    success_url = '/'


class ProductUpdate(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['product_name', "description", "price", "stock"]
    template_name = 'product_update_form.html'
    success_url = '/'


class ProductPurchaseView(LoginRequiredMixin,CreateView):
    form_class = PurchaseCreationForm
    model = Purchase
    success_url = '/cabinet/'
    http_method_names = ['post']

    def form_valid(self, form):
        user = self.request.user
        product_id = self.request.POST.get('user_products')

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return HttpResponseBadRequest("Product not found")

        if product.stock < form.cleaned_data['product_quantity']:
            return HttpResponseBadRequest("Insufficient items in stock")

        total_price = product.price * form.cleaned_data['product_quantity']
        if user.wallet < total_price:
            return HttpResponseBadRequest("Insufficient funds")
        with transaction.atomic():
            purchase = form.save(commit=False)
            purchase.user = self.request.user
            purchase.product = product
            purchase.save()

            product.stock -= form.cleaned_data['product_quantity']
            user.wallet -= total_price
            product.save()
            user.save()

        return super().form_valid(form=form)


class RefundRequestView(View):
    def post(self, request, purchase_id):
        try:
            refund_purchase = Purchase.objects.get(pk=purchase_id)
        except Purchase.DoesNotExist:
            return HttpResponseBadRequest("Purchase not found")

        if refund_purchase.is_refundable:
            refund_request = Refund(refund_purchase=refund_purchase)
            refund_request.save()
            return HttpResponse("Refund request sent successfully")
        else:
            return HttpResponseBadRequest("Refund request is not available at this time")


class RefundListView(LoginRequiredMixin, ListView):
    model = Refund
    template_name = 'refund_requests.html'
    context_object_name = 'refunds'
    login_url = 'login/'


class RefundProcessing(View):

    def post(self, request, refund_id):
        try:
            refund = Refund.objects.get(pk=refund_id)
        except Refund.DoesNotExist:
            return HttpResponseBadRequest("Refund not found")

        action = request.POST.get('action')

        if action == "confirm":
            refund.refund_purchase.product.stock += refund.refund_purchase.product_quantity
            refund.refund_purchase.product.save()

            refund.refund_purchase.user.wallet += (
                        refund.refund_purchase.product.price * refund.refund_purchase.product_quantity)
            refund.refund_purchase.user.save()

            refund.delete()

            return HttpResponseRedirect('/refunds')

        elif action == "reject":
            refund.delete()
            return HttpResponseRedirect('/refunds')


class UserCabinetView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'user_purchases.html'
    context_object_name = 'purchases'
    login_url = 'login/'

    def get_queryset(self):
        user = self.request.user
        return Purchase.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Login(LoginView):
    success_url = '/'
    template_name = 'login.html'

    def get_success_url(self):
        return self.success_url


class Register(CreateView):
    form_class = CustomerForm
    template_name = 'registration_page.html'
    success_url = '/'


class Logout(LoginRequiredMixin, LogoutView):
    next_page = '/'
    login_url = 'login/'


