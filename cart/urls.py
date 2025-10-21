from django.urls import path
from .views import CartListView, CartAddView, CartDeleteView, checkout

app_name = 'cart'

urlpatterns = [
  path('', CartListView.as_view(), name = 'cart_list'),
  path('add/<int:product_id>/', CartAddView.as_view(), name = 'cart_add'),
  path('delete/<int:product_id>/', CartDeleteView.as_view(), name = 'cart_delete'),
  path('checkout/', checkout, name = 'checkout')
]
