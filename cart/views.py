from django.views.generic.list import ListView
from django.views import View
from products.models import Product
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError
from django.urls import reverse

from django.contrib import messages
from order.forms import CheckoutForm
from django.db.models import F

from .models import Cart, CartItem
from order.models import OrderItem

from django.core.mail import send_mail
from django.conf import settings

from django.db import transaction


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
      'form': CheckoutForm()
    })
    return context

class CartAddView(View):
  # データを変更するのでpost()をオーバーライド
  def post(self, request, product_id):
    if not request.session.session_key:
      request.session.create()

    cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

    product = get_object_or_404(Product, pk=product_id) # Product モデルから主キーに一致するレコードを探し、見つからなければ404 Not Found エラーを返す

    if product.stock <= 0:
      messages.error(request, f'{product.name}は在庫切れです')
      return redirect(request.META.get('HTTP_REFERER', reverse('products:product_list')))

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

    # 購入数量が在庫を超えないかチェック
    if created:
      new_quantity = quantity
    else:
      new_quantity = cart_item.quantity + quantity

    if new_quantity > product.stock:
      messages.error(request, f'{product.name}は在庫が足りません（在庫：{product.stock}個）')
      return redirect(request.META.get('HTTP_REFERER', reverse('products:product_list')))

    cart_item.quantity = new_quantity
    cart_item.save()

    messages.success(request, f'{product.name}を{quantity}個カートに追加しました')
    return redirect(request.META.get('HTTP_REFERER', reverse('products:product_list')))

class CartDeleteView(View): # DeleteViewは確認画面つき
  def post(self, request, product_id):
    if not request.session.session_key:
      request.session.create()

    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()

    return redirect('cart:cart_list')

def checkout(request):
  session_key = request.session.session_key
  cart = get_object_or_404(Cart, session_key=session_key)
  cart_items = cart.cartitem_set.select_related('product')

  if request.method == 'POST':
    form = CheckoutForm(request.POST) # リクエストデータをフォームに流し込む
    if not cart_items.exists():
      form.add_error(None, ValidationError('カートに商品が入っていません'))
    elif form.is_valid(): # バリデーションチェック
      with transaction.atomic(): # ここからトランザクション設定
        order = form.save(commit=False)
        order.total_price = 0  # order を.save()して使うために仮で設定
        order.save()

        total_price = 0

        # 在庫チェック
        for item in cart_items:
          if item.product.stock < item.quantity:
            form.add_error(None, f'{item.product.name}の在庫がありません')

            total_quantity = 0
            total_price = 0
            for item in cart_items:
              total_quantity += item.quantity
              total_price += item.product.price * item.quantity

            context = {
              'form': form,
              'cart_items': cart_items,
              'total_quantity': total_quantity,
              'total_price': total_price,
            }

            return render(request, 'cart/cart.html', context)

        # 購入時点のデータを保存（明細に使う）
        for item in cart_items:
          # 小計を変数に保存（足し合わせていくのに使う）
          subtotal_price = item.product.price * item.quantity

          # 小計を合計に加算
          total_price += subtotal_price

          # OrderItemとして保存
          OrderItem.objects.create(
            order=order,
            product_id=item.product.id,
            product_name=item.product.name,
            product_price=item.product.price,
            quantity=item.quantity,
            subtotal_price=subtotal_price,
          )

          # 在庫を減らす
          item.product.stock -= item.quantity
          item.product.save()

        order.total_price = total_price
        order.save()

        # カートを空にする
        cart.cartitem_set.all().delete()

        transaction.on_commit(lambda: send_order_email(order)) # commitされた場合に遅延実行のためlambda関数

      messages.success(request, '購入ありがとうございます！確認メールを送信しました。')
      return redirect('products:product_list')
    
  else:
    form = CheckoutForm()

  # カートが空の時、バリデーションに失敗した時、ページを開いた時のcontextを作成

  cart_items_data = []
  total_quantity = 0
  total_price = 0

  for item in cart_items:
    subtotal_price = item.product.price * item.quantity
    cart_items_data.append({
      'product': item.product,
      'quantity': item.quantity,
      'subtotal_price': subtotal_price,
    })
    total_quantity += item.quantity
    total_price += item.product.price * item.quantity

  context = {
    'form': form,
    'cart_items': cart_items,
    'total_quantity': total_quantity,
    'total_price': total_price,
  }

  return render(request, 'cart/cart.html', context)

def send_order_email(order):
  # メール送信
  subject = '【django_ec】ご注文ありがとうございます'
  message = f'''
  {order.last_name} {order.first_name} 
  ご注文ありがとうございます
  注文番号: {order.id}
  合計金額: {order.total_price}
  ご注文内容:
  '''
  
  for item in order.orderitem_set.all():
    message += f'・{item.product_name} × {item.quantity}点 ({item.subtotal_price}円) \n'
  
  send_mail(
    subject=subject,
    message=message,
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[order.email],
  )