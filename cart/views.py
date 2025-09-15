from django.views.generic.list import ListView
from django.views import View
from products.models import Product
# from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

# Create your views here.
class CartListView(ListView):
  def get(self, request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(pk__in=cart.keys())

    cart_items = []
    for p in products:
      quantity = cart[str(p.pk)] # 数量
      total = p.price * quantity # 小計
      cart_items.append({
        'product': p,
        'quantity': quantity,
        'total': total,
      })
    
    total_quantity = 0
    for cart_item in cart_items:
      total_quantity += cart_item['quantity']

    total_price = 0
    for cart_item in cart_items:
      total_price += cart_item['total']
      
    context = {
      'cart_items': cart_items,
      'total_quantity': total_quantity,
      'total_price': total_price,
    }
      
    return render(request, 'cart/cart.html', context)

class CartAddView(View):
  def post(self, request, product_id):
    product = get_object_or_404(Product, pk=product_id) # Product モデルから主キーに一致するレコードを探し、見つからなければ404 Not Found エラーを返す
    cart = request.session.get('cart', {}) # セッションに cart があるか確認して、なければ空の辞書を返す
    quantity_str = request.POST.get('quantity', 1)

    try:
      quantity = int(quantity_str)
    except ValueError:
      quantity = 1

    product_id_str = str(product_id)

    if product_id_str in cart:
      cart[product_id_str] += quantity
    else:
      cart[product_id_str] = quantity

    request.session['cart'] = cart # cartの変更をセッションに反映
    return redirect('cart:cart_list')

class CartDeleteView(View): # データベースから削除するわけではないのでDeleteViewは使用しない
  def post(self, request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
      del cart[product_id_str]
      request.session['cart'] = cart

    return redirect('cart:cart_list')
  