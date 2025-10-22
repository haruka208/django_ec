from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
  class Meta:
    model = Order
    fields = ['last_name', 'first_name', 'user_name', 'email', 'postal_code', 'prefecture', 'address_1', 'address_2', 'cc_name', 'cc_number', 'cc_expiration', 'cc_cvv']
    widgets = {
      'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '山田'}),
      'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '花子'}),
      'user_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '例：hanako_123'}),
      'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@example.com'}),

      'postal_code': forms.TextInput(attrs={'class':'form-control', 'placeholder': '例：123-4567'}),
      'prefecture': forms.Select(attrs={'class':'form-select'}),
      'address_1': forms.TextInput(attrs={'class':'form-control', 'placeholder': '千代田区丸の内 1-1-1'}),
      'address_2': forms.TextInput(attrs={'class':'form-control', 'placeholder': '丸の内ビルディング 101号室'}),

      'cc_name': forms.TextInput(attrs={'class':'form-control', 'placeholder': '例：HANAKO YAMADA'}),
      'cc_number': forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '例：0000 1111 2222 3333'}),
      'cc_expiration': forms.TextInput(attrs={'class':'form-control', 'placeholder': '例：01/25'}),
      'cc_cvv': forms.PasswordInput(attrs={'class':'form-control', 'placeholder': '例：123'}),
    }
    error_messages = {
      'last_name': {
        'required': '姓を入力してください',
      },
      'first_name': {
        'required': '名を入力してください',
      },
      'user_name': {
        'required': 'ユーザー名を入力してください',
      },
      'email': {
        'required': 'メールアドレスを入力してください',
      },
      'postal_code': {
        'required': '郵便番号を入力してください',
      },
      'prefecture': {
        'required': '都道府県を選択してください',
      },
      'address_1': {
        'required': '住所を入力してください',
      },
      'cc_name': {
        'required': 'カードに記載されている氏名を入力してください',
      },
      'cc_number': {
        'required': 'クレジットカード番号を入力してください',
      },
      'cc_expiration': {
        'required': '有効期限を入力してください',
      },
      'cc_cvv': {
        'required': 'セキュリティコードを入力してください',
      },
    }