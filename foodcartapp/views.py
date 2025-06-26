import json

import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from .models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response


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


def validate_products(products):

    if products is None:
        return {'products': 'Это поле не может быть пустым.'}

    if not isinstance(products, list):
        return {'products': 'Поле должно быть списком'}

    if not products:
        return {'products': 'Этот список не может быть пустым.'}

    for item in products:
        if not isinstance(item, dict):
            return {'products': "Каждый элемент списка должен быть словарем."}

        if 'product' not in item or 'quantity' not in item:
            return {'products': "Каждая товарная позиция должна содержать 'продукт' и 'количество'"}

        if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
            return {'products': "Поле quantity должно быть положительным целым числом."}

        if not isinstance(item['product'], int):
            return {'products': "Поле product должно содержать целочисленный идентификатор"}

        if not Product.objects.filter(id=item['product']).exists():
            return {'products': f"Недопустимы первичный ключ '{item['product']}' "}

    return None


@api_view(['GET', 'POST'])
def register_order(request):

    order_info = request.data
    errors = {}

    if 'products' not in order_info:
        errors['products'] = 'Обязательное поле'
    else:
        product_errors = validate_products(order_info['products'])
        if product_errors:
            errors.update(product_errors)

    required_fields = {
        'firstname': 'Это поле обязательно для заполнения',
        'lastname': 'Это поле обязательно для заполнения',
        'phonenumber': 'Это поле обязательно для заполнения',
        'address': 'Это поле обязательно для заполнения'
    }

    for field in required_fields:
        if field not in order_info:
            errors[field] = 'Обязательное поле '
        else:
            value = order_info[field]
            if value is None or (isinstance(value, str) and not value.strip()):
                errors[field] = 'Это поле не может быть пустым.'
            elif not isinstance(value, str):
                errors[field] = 'Not a valid string.'

    phone = order_info.get('phonenumber')
    if isinstance(phone, str) and phone.strip():
        try:
            number = phonenumbers.parse(phone, 'RU')
            if not phonenumbers.is_valid_number(number):
                errors['phonenumber'] = 'Введен некорректный номер телефона.'
        except phonenumbers.NumberParseException:
            errors['phonenumber'] = 'Введен некорректный номер телефона.'

    if errors:
        return Response(errors, status=400)

    order = Order.objects.create(
        first_name=order_info['firstname'],
        last_name=order_info['last_name'],
        phone_number=order_info['phonenumber'],
        address=order_info['address']
    )

    for item in order_info['products']:
        product = Product.objects.get(id=item['product'])
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity']
        )

    return Response({'status': 'ok'})
