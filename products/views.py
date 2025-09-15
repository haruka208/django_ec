from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Product
# from django.http import HttpResponse

# Create your views here.
class ProductListView(ListView):
  model = Product
  template_name = 'products/product_list.html'

class ProductDetailView(DetailView):
  model = Product
  template_name = 'products/product_detail.html'

  def get_context_data(self,**kwargs):
    context = super().get_context_data(**kwargs)
    context['related_products'] = Product.objects.order_by('-created_at')
    return context