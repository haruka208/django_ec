def cart_total_quantity(request):
  cart = request.session.get('cart', {})
  total_quantity = sum(cart.values())
  return {'cart_total_quantity': total_quantity}