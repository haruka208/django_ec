from django.views.generic.list import ListView
from django.views import View
from products.models import Product
from django.shortcuts import get_object_or_404, redirect
from django.db.models import F

from .models import Cart, CartItem

# Create your views here.
class CartListView(ListView):
  model = CartItem
  template_name = 'cart/cart.html'

  # デフォルトでは 全部のレコードが対象なのでセッションが一致するカートに絞る
  def get_queryset(self):
    if not self.request.session.session_key: # セッションキーがなければ作る
      self.request.session.create()
  
    cart, created = Cart.objects.get_or_create(session_key=self.request.session.session_key) # セッションキーが一致するカートを持ってくる、なければカートを作る
    return cart.cartitem_set.select_related('product') # 関連するProductのデータも一緒にJOINしてカートの一覧を返す（N＋1回避）
  
  # テンプレートに渡す追加のコンテキストを追加する
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs) # 親クラスが用意した標準のコンテキストを取ってくる
    cart, _ = Cart.objects.get_or_create(session_key=self.request.session.session_key)

    total_quantity = 0
    total_price = 0
    cart_items = []
    for item in cart.cartitem_set.all():
      total_quantity += item.quantity
      total_price += item.product.price * item.quantity
      subtotal_price = item.product.price * item.quantity
      cart_items.append({
        'product': item.product,
        'quantity': item.quantity,
        'subtotal_price': subtotal_price,
      })

    context.update({
      'cart_items': cart_items,
      'total_quantity': total_quantity,
      'total_price': total_price,
    })
    return context

class CartAddView(View):
  # データを変更するのでpost()をオーバーライド
  def post(self, request, product_id):
    if not request.session.session_key:
      request.session.create()

    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

    product = get_object_or_404(Product, pk=product_id) # Product モデルから主キーに一致するレコードを探し、見つからなければ404 Not Found エラーを返す

    quantity_str = request.POST.get('quantity', 1)
    try:
      quantity = int(quantity_str)
    except ValueError:
      quantity = 1

    # すでにカートに入ってる商品ならそれを引き出してくる、新規なら新しく入れる
    cart_item, created = CartItem.objects.get_or_create(
      cart=cart,
      product=product,
      defaults={'quantity': quantity}
      )
    if not created:
      CartItem.objects.filter(pk=cart_item.pk).update(
        quantity=F('quantity') + quantity
      )

    cart_item.save()

    return redirect('cart:cart_list')

class CartDeleteView(View): # DeleteViewは確認画面つき
  def post(self, request, product_id):
    if not request.session.session_key:
      request.session.create()

    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()

    return redirect('cart:cart_list')
  