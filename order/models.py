from django.db import models
from django.core.validators import RegexValidator
from prefectures import PREFECTURES

# Create your models here.

class Order(models.Model):
  last_name = models.CharField(verbose_name='姓', max_length=50, blank=False, null=False)
  first_name = models.CharField(verbose_name='名', max_length=50, blank=False, null=False)
  user_name = models.CharField(verbose_name='ユーザー名', max_length=20, blank=False, null=False)
  email = models.EmailField(verbose_name='メールアドレス', blank=False, null=False)

  postal_code = models.CharField(verbose_name='郵便番号', max_length=10, blank=False, null=False)
  prefecture = models.CharField(verbose_name='都道府県', max_length=10, blank=False, null=False)
  address_1 = models.CharField(verbose_name='市区町村・番地', max_length=255, blank=False, null=False)
  address_2 = models.CharField(verbose_name='建物名・部屋番号', max_length=255, blank=True, null=True)

  cc_name = models.CharField(verbose_name='カード名義', max_length=50, blank=False, null=False)
  cc_number = models.CharField(verbose_name='クレジットカード番号', max_length=19, blank=False, null=False, validators=[RegexValidator(r'^\d{13,19}$', '13〜19桁の数字を入力してください')])
  cc_expiration = models.CharField(verbose_name='有効期限(MM/YY)', max_length=5, blank=False, null=False)
  cc_cvv = models.CharField(verbose_name='セキュリティコード', max_length=4, blank=False, null=False, validators=[RegexValidator(r'^\d{3,4}$', '3又は4桁の数字を入力してください')])