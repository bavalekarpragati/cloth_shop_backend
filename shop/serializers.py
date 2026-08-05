from rest_framework import serializers
from .models import Category, Size, Color, Product, ProductImage, Sale, UserProfile


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'hex_code']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']


class ProductReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    sizes = SizeSerializer(many=True, read_only=True)
    colors = ColorSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'base_price', 'selling_price',
            'stock', 'low_stock_limit', 'fabric', 'sizes', 'colors', 'images',
            'is_low_stock', 'is_out_of_stock', 'created_at', 'updated_at',
        ]


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'base_price', 'selling_price',
            'stock', 'low_stock_limit', 'fabric', 'sizes', 'colors',
        ]


class SaleReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = [
            'id', 'product', 'product_name_snapshot', 'quantity',
            'base_price_snapshot', 'selling_price_snapshot', 'total_profit',
            'payment_method', 'customer_name', 'customer_phone', 'timestamp',
        ]
        read_only_fields = ['total_profit', 'timestamp']


class SaleWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['id', 'product', 'quantity', 'payment_method', 'customer_name', 'customer_phone']

    def create(self, validated_data):
        product = validated_data['product']
        validated_data['product_name_snapshot'] = product.name
        validated_data['base_price_snapshot'] = product.base_price
        validated_data['selling_price_snapshot'] = product.selling_price
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'role']