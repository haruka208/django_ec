from django import forms
from products.models import Product

class ManageProductForm(forms.ModelForm):
  class Meta:
    model = Product
    fields = '__all__'
    widgets = {
      "sku": forms.TextInput(attrs={"class": "form-control", "placeholder": "BATH-XXX"}),
      "name": forms.TextInput(attrs={"class": "form-control"}),
      "price": forms.TextInput(attrs={"class": "form-control"}),
      "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
      "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
      "stock": forms.NumberInput(attrs={"class": "form-control"}),
    }