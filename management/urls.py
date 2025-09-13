from django.urls import path
from .views import manage_products, ProductCreateView, ProductUpdateView, ProductDeleteView

app_name = 'management'

urlpatterns = [
  path('products/', manage_products, name = 'manage_products'),
  path('products/create/', ProductCreateView.as_view(), name = 'manage_products_create'),
  path('products/<int:pk>/update/', ProductUpdateView.as_view(), name = 'manage_products_update'),
  path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name = 'manage_products_delete'),
]
