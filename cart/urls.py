from django.urls import path
from .views import CartListView, CartAddView, CartDeleteView, checkout, apply_promo, remove_promo

app_name = 'cart'

urlpatterns = [
  path('', CartListView.as_view(), name = 'cart_list'),
  path('add/<int:product_id>/', CartAddView.as_view(), name = 'cart_add'),
  path('delete/<int:product_id>/', CartDeleteView.as_view(), name = 'cart_delete'),
  path('checkout/', checkout, name = 'checkout'),
  path('apply_promo/', apply_promo, name = 'apply_promo'),
  path('remove_promo', remove_promo, name = 'remove_promo')
]
