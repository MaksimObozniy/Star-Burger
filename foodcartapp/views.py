import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Order, OrderItem


@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET', 'POST'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET', 'POST'])
def register_order(request):
    if request.method == 'GET':
        return Response({'info': 'Здесь нужно отправлять POST-запрос с заказом в JSON-формате.'})

    order_info = request.data

    try:
        first_name = order_info.get('firstname')
        last_name = order_info.get('lastname')
        phone = order_info.get('phonenumber')
        address = order_info.get('address')
        products = order_info.get('products')

    except ValueError as e:
        return Response({
            'error': f'Ошибка: {e}'
        })

    order = Order.objects.create(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone,
        address=address
    )

    for item in products:
        product_id = item.get('product')
        product = Product.objects.get(id=product_id)
        quantity = item.get('quantity')

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )
    return Response({})
