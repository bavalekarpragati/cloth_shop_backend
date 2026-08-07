from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from shop.models import Product, ProductImage
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

BG_COLORS = [
    (240, 217, 181), (200, 226, 218), (222, 203, 228),
    (250, 214, 210), (206, 221, 240), (233, 236, 200),
    (245, 224, 178), (210, 233, 224),
]


class Command(BaseCommand):
    help = 'Generates placeholder images for all products that currently have none.'

    def handle(self, *args, **kwargs):
        products = Product.objects.filter(images__isnull=True).distinct()

        if not products.exists():
            self.stdout.write('No products missing images. Nothing to do.')
            return

        self.stdout.write(f'Generating placeholder images for {products.count()} product(s)...')

        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
            small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
        except IOError:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        for product in products:
            bg_color = random.choice(BG_COLORS)
            img = Image.new('RGB', (800, 800), color=bg_color)
            draw = ImageDraw.Draw(img)

            words = product.name.split()
            lines = []
            current_line = ''
            for word in words:
                test_line = f'{current_line} {word}'.strip()
                if draw.textlength(test_line, font=font) > 680:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)

            total_text_height = len(lines) * 40
            y = (800 - total_text_height) // 2 - 20
            for line in lines:
                line_width = draw.textlength(line, font=font)
                x = (800 - line_width) / 2
                draw.text((x, y), line, fill=(50, 50, 50), font=font)
                y += 40

            category_label = product.category.name if product.category else ''
            label_width = draw.textlength(category_label, font=small_font)
            draw.text(((800 - label_width) / 2, 740), category_label, fill=(90, 90, 90), font=small_font)

            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)

            filename = f'{product.id}_placeholder.jpg'
            image_file = ContentFile(buffer.read(), name=filename)

            ProductImage.objects.create(product=product, image=image_file, is_primary=True)
            self.stdout.write(f'  Added image for: {product.name}')

        self.stdout.write(self.style.SUCCESS('Placeholder image generation complete!'))