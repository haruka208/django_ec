from django.urls import path
from cart.views import checkout
from .views import OrderListView, OrderDetailView

app_name = 'order'

urlpatterns = [
  path('', OrderListView.as_view(), name='order_list'),
  path('<int:pk>/', OrderDetailView.as_view(), name='order_detail')
]