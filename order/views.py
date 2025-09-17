from django.views.generic.edit import CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import Order

# Create your views here.
class OrderCreateView(CreateView):
  model = Order
  fields = '__all__'
  template_name = 'cart/cart.html'
  success_url = reverse_lazy('order:order')

  # def form_valid(self, form):
  #   response = super().form_valid(form)
  #   self.request.session['cart'] = {}
  #   messages.success(self.request, 'ご購入ありがとうございました！')
  #   return response