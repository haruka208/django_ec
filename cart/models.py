from django.db import models
from products.models import Product

# Create your models here.

class Cart(models.Model):
  session_key = models.CharField (verbose_name='セッションキー', max_length=40, unique=True)
  created_at = models.DateTimeField(verbose_name='作成日',auto_now_add=True)
  updated_at = models.DateTimeField(verbose_name='更新日',auto_now=True)

  def __str__(self):
    return f'セッションキー : {self.session_key})'

  class Meta:
    db_table = 'cart'

class CartItem(models.Model):
  cart = models.ForeignKey(Cart, verbose_name='カート',on_delete=models.CASCADE)
  product = models.ForeignKey(Product, verbose_name='商品',on_delete=models.CASCADE)
  quantity = models.PositiveIntegerField(verbose_name='数量',default=1)

  def __str__(self):
    return f'{self.product.name} × {self.quantity}点'

  class Meta:
    db_table = 'cart_item'
    constraints = [
      models.UniqueConstraint(
        fields=['cart', 'product'],
        name='unique_cart_product',
        )
    ]
