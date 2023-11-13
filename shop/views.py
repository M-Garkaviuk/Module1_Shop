from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from shop.models import Product, Purchase, Refund
from shop.forms import CustomerForm, ProductForm, PurchaseCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView
from django.db import transaction
from django.contrib import messages


class AdminLoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ProductListView(ListView):
    model = Product
    template_name = 'index.html'
    login_url = 'login/'
    extra_context = {'purchase_form': PurchaseCreationForm()}


class ProductCreateView(AdminLoginRequiredMixin, CreateView):
    template_name = 'new_product.html'
    login_url = 'login/'
    http_method_names = ['get', 'post']
    form_class = ProductForm
    success_url = '/'

    def form_valid(self, form):
        response = super().form_valid(form)
        product_name = form.cleaned_data.get('product_name')
        messages.success(self.request, f'Product "{product_name}" created successfully.')
        return response


class ProductUpdate(AdminLoginRequiredMixin, UpdateView):
    model = Product
    fields = ['product_name', "description", "price", "stock"]
    template_name = 'product_update_form.html'

    def form_valid(self, form):
        with transaction.atomic():
            product = form.save(commit=False)
            product.save()
            messages.success(self.request, f'Product "{product.product_name}" updated successfully.')
            return super().form_valid(form)

    def get_success_url(self):
        return reverse("index")


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
            messages.success(self.request, f'You have successfully bought "{product.product_name}"! Thank you! ')

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
            messages.success(self.request, f'Refund request has been submitted successfully ')

        else:
            return HttpResponseBadRequest("Refund request is not available at this time")

        return redirect('user-cabinet')


class RefundListView(AdminLoginRequiredMixin, ListView):
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
            with transaction.atomic():
                refund.refund_purchase.product.stock += refund.refund_purchase.product_quantity
                refund.refund_purchase.product.save()

                refund.refund_purchase.user.wallet += (
                        refund.refund_purchase.product.price * refund.refund_purchase.product_quantity)
                refund.refund_purchase.user.save()

                refund.delete()
                messages.success(self.request, f'Refund request has been approved successfully')

            return HttpResponseRedirect('/refunds')

        elif action == "reject":
            refund.delete()
            messages.success(self.request, f'Refund request has been deleted successfully')
            return HttpResponseRedirect('/refunds')


class UserCabinetView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'user_purchases.html'
    context_object_name = 'purchases'
    login_url = 'login/'

    def get_queryset(self):
        user = self.request.user
        return Purchase.objects.filter(user=user)


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

