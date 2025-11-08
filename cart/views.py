from django.views.generic.list import ListView
from django.views import View
from products.models import Product

from django.contrib import messages
from order.forms import CheckoutForm
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError
from django.urls import reverse

from .models import Cart, CartItem
from order.models import OrderItem

from django.core.mail import send_mail
from django.conf import settings

from django.db import transaction

from promotion.models import PromotionCode
  

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
    session = self.request.session

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

    # 🎟️セッションからプロモ情報を取得
    applied_promo_code = session.get('applied_promo_code')
    applied_discount = session.get('applied_discount', 0) or 0

    # 🧹カートが空ならプロモをリセット
    if not cart_items:
      session.pop('applied_promo_code', None)
      session.pop('applied_discount', None)
      applied_promo_code = None
      applied_discount = 0

    final_total = total_price - applied_discount

    context.update({
      'cart_items': cart_items,
      'total_quantity': total_quantity,
      'total_price': total_price,
      'form': CheckoutForm(),
      'applied_promo_code': applied_promo_code,
      'applied_discount': applied_discount,
      'final_total': final_total,
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
    # if not created:
    #   CartItem.objects.filter(pk=cart_item.pk).update(
    #     quantity=F('quantity') + quantity
    #   )

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
  
def remove_promo(request):
  # 安全のため POSTメソッド に限定
  if request.method == 'POST':
      request.session.pop('applied_promo_code', None)
      request.session.pop('applied_discount', None)
      messages.info(request, 'プロモーションコードを解除しました')
  return redirect('cart:cart_list')

def apply_promo(request):
    # GET/POSTどっちでも拾えるようにしておく
    raw_code = (request.GET.get('promotion_code')
                or request.POST.get('promotion_code')
                or '').strip()
    if not raw_code:
        messages.error(request, 'プロモーションコードを入力してください')
        return redirect('cart:cart_list')

    # セッションキー確保
    if not request.session.session_key:
        request.session.create()

    # カートが存在することだけ確認（ここでは合計計算しない）
    cart = get_object_or_404(Cart, session_key=request.session.session_key)

    # 大文字小文字を無視して有効なコードを検索
    try:
        promo = PromotionCode.objects.get(code__iexact=raw_code, is_used=False)
    except PromotionCode.DoesNotExist:
        # 無効ならセッション上の前回適用もクリアしておくと親切
        request.session.pop('applied_promo_code', None)
        request.session.pop('applied_discount', None)
        messages.error(request, 'このプロモーションコードは無効または使用済みです')
        return redirect('cart:cart_list')

    # セッションに保存（この時点では is_used は更新しない！）
    request.session['applied_promo_code'] = promo.code  # 実際の表記で保存
    request.session['applied_discount'] = int(promo.discount_amount)

    messages.success(request, f'プロモーションコード {promo.code} を適用しました！（{promo.discount_amount}円引き）')
    return redirect('cart:cart_list')

def checkout(request):
  promo_obj = None # 後でモデルを入れる場所を確保（安全のための初期化（GET時に必要））

  session_key = request.session.session_key
  cart = get_object_or_404(Cart, session_key=session_key)
  cart_items = cart.cartitem_set.select_related('product')

  if request.method == 'POST':
    form = CheckoutForm(request.POST) # リクエストデータをフォームに流し込む

    # カートが空ならエラーを追加して戻す
    if not cart_items.exists():
      request.session['checkout_form_data'] = request.POST.dict()

      messages.error(request, 'カートに商品が入っていません')

      context = {
        'form': form,
        'cart_items': cart_items,
        'total_quantity': 0,
        'total_price': 0,
      }

      return render(request, 'cart/cart.html', context)
    
    # フォームが有効な場合（購入処理）
    elif form.is_valid(): # バリデーションチェック

      with transaction.atomic(): # ここからトランザクション設定
        order = form.save(commit=False)
        # order.total_price = 0  # order を.save()して使うために仮で設定　→ モデルにデフォルト値を追加して削除
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

          # プロモコード適用🎟️（セッション使用）
          promo_code = request.session.get('applied_promo_code')
          discount = request.session.get('applied_discount', 0)

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

        order.promo_code = promo_code
        order.discount = discount
        order.total_price = total_price - discount
        order.save()

        if promo_code:
          PromotionCode.objects.filter(code=promo_code).update(is_used=True)

        # カートを空にする
        cart.cartitem_set.all().delete()

        transaction.on_commit(lambda: send_order_email(order)) # commitされた場合に遅延実行のためlambda関数

        if 'checkout_form_data' in request.session:
          del request.session['checkout_form_data']

      messages.success(request, '購入ありがとうございます！確認メールを送信しました。')
      return redirect('products:product_list')
    
    # フォームが無効の場合（入力エラーなど）
    else:
      messages.error(request, '入力内容に誤りがあります。確認してください。')
      request.session['checkout_form_data'] = request.POST.dict()

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
  
  # GETリクエストの時
  else:
    # セッションの入力内容を復元
    form_data = request.session.get('checkout_form_data')
    if form_data:
      form = CheckoutForm(initial=form_data) # initial=は初期値
    else:
      form = CheckoutForm()

    # カートが空の時、バリデーションに失敗した時、ページを開いた時のcontextを作成

    # 🛒カートの情報をcontextに渡す
    # cart_items_data = [] → テンプレートに渡していなかったので削除
    total_quantity = 0
    total_price = 0

    for item in cart_items:
      # subtotal_price = item.product.price * item.quantity　→　ここでは不要なので削除
      # cart_items_data.append({
      #   'product': item.product,
      #   'quantity': item.quantity,
      #   'subtotal_price': subtotal_price,
      # })
      total_quantity += item.quantity
      total_price += item.product.price * item.quantity

    context = {
      'form': form,
      'cart_items': cart_items,
      'total_quantity': total_quantity,
      'total_price': total_price,
      'applied_promo': promo_obj,
    }

    return render(request, 'cart/cart.html', context)

def send_order_email(order):
  # メール送信
  subject = '【Calm Bath】ご注文ありがとうございます'

  message = f'''
  {order.last_name} {order.first_name} 様

  このたびは Calm Bath をご利用いただき誠にありがとうございます。
  以下の内容でご注文を承りました。


  【注文番号】 {order.id}
  【注文日時】 {order.created_at}
  【購入者名】 {order.last_name} {order.first_name}
  【ユーザー名】 @{order.user_name}
  【メールアドレス】 {order.email}


  【お届け先】
  〒{order.postal_code}
  {order.get_prefecture_display()}{order.address_1} {order.address_2}


  【クレジットカード情報】
  カード名義：{order.last_name.upper()} {order.first_name.upper()}
  カード番号：**** **** **** {order.cc_number[-4:]}
  有効期限：{order.cc_expiration}


  【ご注文内容】
  '''
  for item in order.orderitem_set.all():
    message += f'・{item.product_name} × {item.quantity}点 {item.subtotal_price}円 \n'

  message += f'''

  【プロモーションコード割引】
  プロモーションコード：{order.promo_code}
  割引金額：{order.discount}円


  【合計金額】
  合計金額：{order.total_price:,}円


  ────────────────────────────
  このメールはご注文受付の自動送信メールです。


  Calm Bath
  '''

  send_mail(
    subject=subject,
    message=message,
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[order.email],
  )
