from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from shop.models import Category, Size, Color, Product, Sale
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seeds the database with categories, sizes, colors, users, products, and mock sales data.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # 1. Users
        self.stdout.write('Creating users...')
        owner_user, created = User.objects.get_or_create(username='owner', email='owner@clothshop.com')
        if created:
            owner_user.set_password('owner123')
            owner_user.save()
        owner_user.profile.role = 'OWNER'
        owner_user.profile.save()

        customer_user, created = User.objects.get_or_create(username='customer', email='customer@clothshop.com')
        if created:
            customer_user.set_password('customer123')
            customer_user.save()
        customer_user.profile.role = 'CUSTOMER'
        customer_user.profile.save()

        self.stdout.write('  owner / owner123')
        self.stdout.write('  customer / customer123')

        # 2. Sizes
        self.stdout.write('Creating sizes...')
        sizes_list = ['S', 'M', 'L', 'XL', 'XXL', '28', '30', '32', '34', '36']
        sizes_objs = {name: Size.objects.get_or_create(name=name)[0] for name in sizes_list}

        # 3. Colors
        self.stdout.write('Creating colors...')
        colors_list = [
            ('Crimson Red', '#DC143C'), ('Navy Blue', '#000080'), ('Emerald Green', '#50C878'),
            ('Midnight Black', '#000000'), ('Soft White', '#FFFDD0'), ('Rose Pink', '#FF007F'),
            ('Marigold Yellow', '#EAA221'), ('Royal Gold', '#D4AF37'), ('Heather Grey', '#808080'),
        ]
        colors_objs = {name: Color.objects.get_or_create(name=name, defaults={'hex_code': hex_code})[0]
                        for name, hex_code in colors_list}

        # 4. Categories
        self.stdout.write('Creating categories...')
        ladies_parent, _ = Category.objects.get_or_create(name='Ladies Wear', parent=None)
        ladies_cats = ['Kurtis', 'Sarees', 'Dresses', 'Jeans']
        ladies_objs = {c: Category.objects.get_or_create(name=c, parent=ladies_parent)[0] for c in ladies_cats}

        kids_parent, _ = Category.objects.get_or_create(name='Kids Wear', parent=None)
        girls_parent, _ = Category.objects.get_or_create(name='Girls', parent=kids_parent)
        girls_cats = ['Frocks', 'Traditional Dresses']
        girls_objs = {c: Category.objects.get_or_create(name=c, parent=girls_parent)[0] for c in girls_cats}

        boys_parent, _ = Category.objects.get_or_create(name='Boys', parent=kids_parent)
        boys_cats = ['Suits', 'Shirts']
        boys_objs = {c: Category.objects.get_or_create(name=c, parent=boys_parent)[0] for c in boys_cats}

        # 5. Products
        self.stdout.write('Creating products...')
        products_data = [
            {'name': 'Elegant Embroidered Silk Kurti', 'description': 'Premium silk kurti with golden embroidery.',
             'category': ladies_objs['Kurtis'], 'base_price': Decimal('850.00'), 'selling_price': Decimal('1699.00'),
             'stock': 25, 'low_stock_limit': 5, 'fabric': 'Silk Blend',
             'sizes': ['M', 'L', 'XL', 'XXL'], 'colors': ['Marigold Yellow', 'Crimson Red', 'Navy Blue']},

            {'name': 'Royal Banarasi Silk Saree', 'description': 'Handwoven Banarasi saree with zari work.',
             'category': ladies_objs['Sarees'], 'base_price': Decimal('2200.00'), 'selling_price': Decimal('4999.00'),
             'stock': 12, 'low_stock_limit': 3, 'fabric': 'Banarasi Silk',
             'sizes': ['L'], 'colors': ['Royal Gold', 'Crimson Red']},

            {'name': 'Floral Georgette Maxi Dress', 'description': 'Lightweight georgette maxi dress, pastel floral print.',
             'category': ladies_objs['Dresses'], 'base_price': Decimal('600.00'), 'selling_price': Decimal('1299.00'),
             'stock': 30, 'low_stock_limit': 5, 'fabric': 'Georgette',
             'sizes': ['S', 'M', 'L', 'XL'], 'colors': ['Rose Pink', 'Soft White']},

            {'name': 'High-Waist Skinny Fit Denim', 'description': 'Stretchable high-waist jeans.',
             'category': ladies_objs['Jeans'], 'base_price': Decimal('700.00'), 'selling_price': Decimal('1599.00'),
             'stock': 4, 'low_stock_limit': 5, 'fabric': 'Cotton Denim Stretch',
             'sizes': ['28', '30', '32'], 'colors': ['Navy Blue', 'Heather Grey']},

            {'name': 'Girls Festive Tutu Frock', 'description': 'Pink layered net tutu frock with sequined bodice.',
             'category': girls_objs['Frocks'], 'base_price': Decimal('450.00'), 'selling_price': Decimal('999.00'),
             'stock': 15, 'low_stock_limit': 4, 'fabric': 'Net & Satin',
             'sizes': ['S', 'M', 'L'], 'colors': ['Rose Pink', 'Soft White']},

            {'name': 'Girls Traditional Lehanga Choli', 'description': 'Ethnic lehenga choli set with mirror details.',
             'category': girls_objs['Traditional Dresses'], 'base_price': Decimal('900.00'), 'selling_price': Decimal('1999.00'),
             'stock': 8, 'low_stock_limit': 2, 'fabric': 'Cotton Silk',
             'sizes': ['M', 'L', 'XL'], 'colors': ['Marigold Yellow', 'Crimson Red']},

            {'name': 'Boys Formal Blazer Suit Set', 'description': '3-piece formal suit with bow tie.',
             'category': boys_objs['Suits'], 'base_price': Decimal('1500.00'), 'selling_price': Decimal('3299.00'),
             'stock': 0, 'low_stock_limit': 3, 'fabric': 'Premium Viscose Blend',
             'sizes': ['M', 'L', 'XL'], 'colors': ['Navy Blue', 'Midnight Black']},

            {'name': 'Boys Striped Cotton Shirt', 'description': 'Casual long-sleeve cotton striped shirt.',
             'category': boys_objs['Shirts'], 'base_price': Decimal('300.00'), 'selling_price': Decimal('699.00'),
             'stock': 40, 'low_stock_limit': 6, 'fabric': '100% Organic Cotton',
             'sizes': ['S', 'M', 'L'], 'colors': ['Soft White', 'Navy Blue']},
        ]

        created_products = []
        for p_data in products_data:
            sizes = p_data.pop('sizes')
            colors = p_data.pop('colors')
            prod, _ = Product.objects.get_or_create(name=p_data['name'], defaults=p_data)
            for sz in sizes:
                prod.sizes.add(sizes_objs[sz])
            for cl in colors:
                prod.colors.add(colors_objs[cl])
            prod.save()
            created_products.append(prod)
            self.stdout.write(f"Product: {prod.name} (Stock: {prod.stock})")

        # 6. Mock Sales
        self.stdout.write('Generating mock sales data...')
        payment_options = ['CASH', 'CARD', 'UPI']
        customers = [
            ('Amit Sharma', '9876543210'), ('Priya Patel', '9823456789'),
            ('Rajesh Kumar', '9712345678'), ('Sunita Gupta', '9988776655'), ('', ''),
        ]
        now = timezone.now()
        sales_count = 0

        for i in range(45):
            days_ago = random.randint(0, 30)
            sale_time = now - timezone.timedelta(days=days_ago, hours=random.randint(1, 10))
            product = random.choice(created_products)
            quantity = random.randint(1, 3)
            payment = random.choice(payment_options)
            cust_name, cust_phone = random.choice(customers)

            sale = Sale(
                product=product, product_name_snapshot=product.name, quantity=quantity,
                base_price_snapshot=product.base_price, selling_price_snapshot=product.selling_price,
                payment_method=payment, customer_name=cust_name, customer_phone=cust_phone,
            )
            sale.total_profit = (sale.selling_price_snapshot - sale.base_price_snapshot) * sale.quantity
            sale.timestamp = sale_time
            super(Sale, sale).save()
            Sale.objects.filter(pk=sale.pk).update(timestamp=sale_time)
            sales_count += 1

        self.stdout.write(f"Successfully generated {sales_count} mock sales records.")
        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
