from django.shortcuts import render
from shop.models import Product
from django.views.generic.base import TemplateView
from shop.forms import CustomerForm, ProductForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import ListView, CreateView, UpdateView


class HomePageView(TemplateView):
    template_name = "index.html"
    http_method_names = ['get', "post"]

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()[:10]

    def get(self, request, *args, **kwargs):
        print("123")
        return render(request, 'index.html')


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = 'new_product.html'
    login_url = 'login/'
    http_method_names = ['get', 'post']
    form_class = ProductForm
    success_url = '/'

    # def form_valid(self, form):
    #     obj = form.save(commit=False)
    #     print(obj)
    #     obj.save()
    #     return super().form_valid(form=form)


class ProductListView(ListView):
    model = Product
    template_name = 'index.html'
    login_url = 'login/'


class ProductUpdate(UpdateView):
    model = Product
    fields = ['product_name', "description", "price", "stock"]
    template_name = 'product_update_form.html'
    success_url = '/'


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


