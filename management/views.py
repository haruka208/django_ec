from django.views.generic.edit import CreateView, UpdateView, DeleteView
from products.models import Product
# from django.http import HttpResponse

from basicauth.decorators import basic_auth_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.urls import reverse_lazy
from .forms import ManageProductForm

# Create your views here. 
@basic_auth_required
def manage_products(request):
  products = Product.objects.all()
  return render(request, 'management/products/manage_products.html',{
    "products":products
  })

@method_decorator(basic_auth_required, name="dispatch")
class ProductCreateView(CreateView):
  # model = Product # モデル用のフォームを自動で用意
  # fields = '__all__' # フォームに表示するフィールド
  form_class = ManageProductForm # フォームで明示的に指定
  template_name = "management/products/manage_products_create.html" # 指定したテンプレートでフォームを表示
  success_url = reverse_lazy("management:manage_products")

@method_decorator(basic_auth_required, name="dispatch")
class ProductUpdateView(UpdateView):
  model = Product
  form_class = ManageProductForm
  template_name = "management/products/manage_products_update.html"
  success_url = reverse_lazy("management:manage_products")

@method_decorator(basic_auth_required, name="dispatch")
class ProductDeleteView(DeleteView):
  model = Product
  template_name = "management/products/manage_products_delete.html"
  success_url = reverse_lazy("management:manage_products")