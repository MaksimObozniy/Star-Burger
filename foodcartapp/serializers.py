from rest_framework import serializers
from .models import Order, OrderItem, Product
import phonenumbers


class OrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Количество должно быть положительным')
        return value


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    firstname = serializers.CharField(
        source='first_name',
        error_messages={
            'required': 'Обязательное поле.',
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.'
        }
    )
    lastname = serializers.CharField(
         source='last_name',
        error_messages={
            'required': 'Обязательное поле.',
            'blank': 'Это поле не может быть пустым.',
            'null': 'Это поле не может быть пустым.',
            'invalid': 'Not a valid string.'
        }
    )
    phonenumber = serializers.CharField(
         source='phone_number',
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
        write_only=True,
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

    def create(self, validated_info):
        products_info = validated_info.pop('products')

        order = Order.objects.create(
            first_name=validated_info['first_name'],
            last_name=validated_info['last_name'],
            phone_number=validated_info['phone_number'],
            address=validated_info['address']
        )

        for item in products_info:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity']
            )

        return order
