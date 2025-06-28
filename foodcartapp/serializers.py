from rest_framework import serializers
from .models import Order, OrderItem, Product
import phonenumbers


class OrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        error_messages={
            'required': 'Обязательное поле.',
            'does_not_exist': 'Недопустимый первичный ключ',
            'incorrect_type': 'Неверный тип значения.',
        }
    )
    quantity = serializers.IntegerField(
        error_messages={
            'required': 'Обязательное поле.',
            'invalid': 'Неверное значение количества.',
        }
    )

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество должно быть положительным')
        return value


class OrderSerializer(serializers.Serializer):
    firstname = serializers.CharField(
        error_messages={
            'required': 'Обязательное поле.',
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.'
        }
    )
    lastname = serializers.CharField(
        error_messages={
            'required': 'Обязательное поле.',
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.'
        }
    )
    phonenumber = serializers.CharField(
        error_messages={
            'required': 'Обязательное поле.',
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.'
        }
    )
    address = serializers.CharField(
        error_messages={
            'required': 'Обязательное поле.',
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.'
        }
    )
    products = OrderItemSerializer(
        many=True,
        required=True,
        error_messages={
            'required': 'Обязательное поле.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Ожидался list со значениями.'
        }
    )

    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError('Этот список не может быть пустым.')
        return value

    def validate_phonenumber(self, value):
        try:
            number = phonenumbers.parse(value, 'RU')
            if not phonenumbers.is_valid_number(number):
                raise serializers.ValidationError('Введен некорректный номер телефона.')
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError('Введен некорректный номер телефона.')
        return value

    def create(self, validated_data):
        order = Order.objects.create(
            first_name=validated_data['firstname'],
            last_name=validated_data['lastname'],
            phone_number=validated_data['phonenumber'],
            address=validated_data['address']
        )
        for item in validated_data['products']:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity']
            )
        return order
