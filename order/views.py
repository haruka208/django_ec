from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from cart.models import Cart
from order.models import Order, OrderItem
from .forms import CheckoutForm

from basicauth.decorators import basic_auth_required
from django.utils.decorators import method_decorator

# Create your views here.

# def cancel_order(request, order_id):
#   order = get_object_or_404(Order, id=order_id)
#   order.cancel()

@method_decorator(basic_auth_required, name='dispatch')
class OrderListView(ListView):
  model = Order
  template_name = 'order/order_list.html'

@method_decorator(basic_auth_required, name='dispatch')
class OrderDetailView(DetailView):
  model = Order
  template_name = 'order/order_detail.html'
