# from order.models import Order, OrderItem, Cart
# from django.db import transaction
# from rest_framework.exceptions import PermissionDenied, ValidationError
# from users.models import User

# class OrderService:
#     @staticmethod
#     def create_order(user_id, cart_id):
#         with transaction.atomic():

#             user = User.objects.select_for_update().get(pk=user_id)

#             # cart = Cart.objects.select_related('user').get(pk=cart_id)
#             # cart_items = cart.items.select_related('product').all()

#             cart = Cart.objects.select_for_update().get(pk=cart_id)
#             cart_items = cart.items.select_related('product').select_for_update()


#             if not cart_items.exists():
#                 raise ValidationError({'detail': 'Cart is empty.'})
#             total_price = 0
#             order_items = []
#             for item in cart_items:
#                 product = item.product

#                 if product.stock < item.quantity:
#                     raise ValidationError({
#                         'detail': f'Insufficient stock for product "{product.name}".'
#                     })
#                 item_total = product.price * item.quantity
#                 total_price += item_total

#                 product.stock -= item.quantity
#                 product.save()
#                 item_total = product.price * item.quantity
#                 total_price += item_total
#                 order_items.append(
#                     OrderItem(
#                         order=None,  
#                         product=product,
#                         price=product.price,
#                         quantity=item.quantity,
#                         total_price=item_total,
#                     )
#                 )
#             order = Order.objects.create(
#                 user_id=user_id,
#                 total_price=total_price
#             )
#             for order_item in order_items:
#                 order_item.order = order
#             OrderItem.objects.bulk_create(order_items)
#             cart.delete()
#             return order

#     @staticmethod
#     def cancel_order(order, user):
#         if user.is_staff:
#             order.status = Order.CANCELED
#             order.save()
#             return order
#         if order.user != user:
#             raise PermissionDenied(
#                 {'detail': 'You can only cancel your own order'}
#             )
#         if order.status == Order.DELIVERED:
#             raise ValidationError(
#                 {'detail': 'You cannot cancel the order after delivery'}
#             )
#         order.status = Order.CANCELED
#         order.save()
#         return order


from order.models import Order, OrderItem, Cart
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from users.models import User


class OrderService:

    @staticmethod
    def create_order(user_id, cart_id):
        with transaction.atomic():

            user = User.objects.select_for_update().get(pk=user_id)
            cart = Cart.objects.select_for_update().get(pk=cart_id)
            cart_items = cart.items.select_related('product').select_for_update()
            if not cart_items.exists():
                raise ValidationError({'detail': 'Cart is empty.'})
            total_price = 0
            order_items = []
            for item in cart_items:
                product = item.product

                if product.stock < item.quantity:
                    raise ValidationError({
                        'detail': f'Insufficient stock for "{product.name}".'
                    })

                item_total = product.price * item.quantity
                total_price += item_total

            if user.balance < total_price:
                raise ValidationError({'detail': 'Insufficient balance.'})

            user.balance -= total_price
            user.save()

            order = Order.objects.create(
                user=user,
                total_price=total_price
            )

            for item in cart_items:
                product = item.product

                product.stock -= item.quantity
                product.save()

                order_items.append(
                    OrderItem(
                        order=order,
                        product=product,
                        price=product.price,
                        quantity=item.quantity,
                        total_price=product.price * item.quantity,
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            cart.delete()

            return order

    @staticmethod
    def cancel_order(order, user):
        with transaction.atomic():

            if not user.is_staff and order.user != user:
                raise PermissionDenied(
                    {'detail': 'You can only cancel your own order'}
                )

            if order.status == Order.DELIVERED:
                raise ValidationError(
                    {'detail': 'Cannot cancel delivered order'}
                )

            if order.status == Order.CANCELED:
                raise ValidationError(
                    {'detail': 'Order already canceled'}
                )

            order.user.balance += order.total_price
            order.user.save()

            for item in order.items.select_related('product'):
                product = item.product
                product.stock += item.quantity
                product.save()

            order.status = Order.CANCELED
            order.save()

            return order