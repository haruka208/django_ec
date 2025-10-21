from django.db import models
from django.core.validators import RegexValidator
from prefectures import PREFECTURES

from products.models import Product

# Create your models here.

class Order(models.Model):
  last_name = models.CharField(verbose_name='姓', max_length=50, blank=False, null=False)
  first_name = models.CharField(verbose_name='名', max_length=50, blank=False, null=False)
  user_name = models.CharField(verbose_name='ユーザー名', max_length=20, blank=False, null=False)
  email = models.EmailField(verbose_name='メールアドレス', blank=False, null=False)

  postal_code = models.CharField(verbose_name='郵便番号', max_length=10, blank=False, null=False)
  prefecture = models.CharField(verbose_name='都道府県', max_length=10, blank=False, null=False, choices=PREFECTURES)
  address_1 = models.CharField(verbose_name='市区町村・番地', max_length=255, blank=False, null=False)
  address_2 = models.CharField(verbose_name='建物名・部屋番号', max_length=255, blank=True, null=True)

  cc_name = models.CharField(verbose_name='カード名義', max_length=50, blank=False, null=False)
  cc_number = models.CharField(verbose_name='クレジットカード番号', max_length=19, blank=False, null=False)
  cc_expiration = models.CharField(verbose_name='有効期限(MM/YY)', max_length=5, blank=False, null=False)
  cc_cvv = models.CharField(verbose_name='セキュリティコード', max_length=4, blank=False, null=False, validators=[RegexValidator(r'^\d{3,4}$', '3又は4桁の数字を入力してください')])

  created_at = models.DateTimeField(auto_now_add=True, verbose_name='注文日時', blank=False, null=False)
  total_price = models.IntegerField(verbose_name='注文金額', blank=False, null=False)

  # STATUS_CHOICES = [
  #   ('pending', '未確定'),
  #   ('paid', '支払い済み'),
  #   ('shipped', '発送済み'),
  #   ('cancelled', 'キャンセル'),
  # ]
  # status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

  def __str__(self):
    return f'注文 : {self.last_name} {self.first_name}({self.total_price}円)'
  
  # def cancel(self):
  #   for item in self.order_items.all():
  #     product = item.product
  #     product.stock += item.quantity # 在庫を差し戻す
  #     product.save()
  #   self.status = 'cancelled'
  #   self.save()


class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='注文情報')
  product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
  # product_id = models.IntegerField(verbose_name='商品ID')
  product_name = models.CharField(verbose_name='商品名', max_length=255)
  product_price = models.IntegerField(verbose_name='価格')
  quantity = models.IntegerField(verbose_name='数量')
  subtotal_price = models.IntegerField(verbose_name='小計')
  def __str__(self):
    return f'注文商品 : {self.product_name} × {self.quantity}点(注文ID : {self.order.id})'