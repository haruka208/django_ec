from django import forms
from django.core.validators import RegexValidator
from .models import Order

class OrderForm(forms.ModelForm):
  cc_number = forms.CharField(
    label='クレジットカード番号',
    max_length=19,
    validators=[RegexValidator(r'^\d{13,19}$', '13〜19桁の数字を入力してください')]
  )

  cc_cvv = forms.CharField(
    label='セキュリティコード',
    max_length=4,
    validators=[RegexValidator(r'^\d{3,4}$', '13桁または4桁の数字を入力してください')]
  )

  class Meta:
    model = Order
    fields = '__all__'