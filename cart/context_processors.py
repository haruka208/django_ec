from cart.models import Cart, CartItem

def cart_total_quantity(request):
  session_key = request.session.session_key
  if not session_key:
    return {'cart_totlal_quantity': 0}
  
  try:
    cart = Cart.objects.get(session_key=session_key)
    cart_items = CartItem.objects.filter(cart=cart)
    total_quantity = 0
    for item in cart_items:
      total_quantity += item.quantity
  except Cart.DoesNotExist:
    total_quantity = 0

  return {'cart_total_quantity': total_quantity}