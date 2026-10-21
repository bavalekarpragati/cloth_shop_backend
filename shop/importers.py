import csv
import io
import os
import zipfile
from decimal import Decimal, InvalidOperation

from django.core.files.base import ContentFile
from django.db import transaction
from openpyxl import load_workbook
from PIL import Image

from .models import Product, ProductImage, Size, Color

MAX_ROWS = 1000
IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.webp')
MAX_IMAGE_BYTES = 5 * 1024 * 1024        # per picture
MAX_ZIP_BYTES = 100 * 1024 * 1024        # all pictures together, unpacked


class ImportFileError(Exception):
    """The whole file is unusable (wrong type, missing columns...)."""


def _clean(value):
    return '' if value is None else str(value).strip()


# ---------------------------------------------------------------- reading the sheet
def read_rows(upload):
    """Return [(line_number, {column: value}), ...] from a .csv or .xlsx upload."""
    filename = upload.name.lower()

    if filename.endswith('.csv'):
        try:
            text = upload.read().decode('utf-8-sig')      # utf-8-sig removes Excel's hidden BOM
        except UnicodeDecodeError:
            raise ImportFileError('Save the CSV as "CSV UTF-8" and try again')
        raw = list(csv.reader(io.StringIO(text)))
    elif filename.endswith('.xlsx'):
        try:
            workbook = load_workbook(upload, read_only=True, data_only=True)
            raw = [list(r) for r in workbook.active.iter_rows(values_only=True)]
        except Exception:
            raise ImportFileError('Could not read this Excel file')
    else:
        raise ImportFileError('Upload a .csv or .xlsx file')

    if not raw:
        raise ImportFileError('The file is empty')

    headers = [_clean(h).lower().replace(' ', '_') for h in raw[0]]
    missing = [h for h in ('name', 'selling_price') if h not in headers]
    if missing:
        raise ImportFileError(f"Missing column(s): {', '.join(missing)}")

    rows = []
    for line, values in enumerate(raw[1:], start=2):       # line 2 = first data row
        record = {h: _clean(v) for h, v in zip(headers, values)}
        if any(record.values()):                           # skip blank lines
            rows.append((line, record))

    if len(rows) > MAX_ROWS:
        raise ImportFileError(f'Too many rows (limit is {MAX_ROWS} per file)')
    return rows


# ---------------------------------------------------------------- reading the images ZIP
def open_image_zip(upload):
    """Open the ZIP and index its pictures by lowercase file name. Nothing is unpacked to disk."""
    try:
        zf = zipfile.ZipFile(upload)
    except zipfile.BadZipFile:
        raise ImportFileError('The images file is not a valid ZIP')

    lookup, total = {}, 0
    for info in zf.infolist():
        base = os.path.basename(info.filename)
        # skip folders, hidden files and the "__MACOSX/._photo.jpg" junk that Mac zips contain
        if info.is_dir() or base.startswith(('.', '_')) or not base.lower().endswith(IMAGE_EXTS):
            continue
        total += info.file_size
        lookup.setdefault(base.lower(), info)

    if not lookup:
        raise ImportFileError('No .jpg, .png or .webp pictures found in the ZIP')
    if total > MAX_ZIP_BYTES:
        raise ImportFileError('The images ZIP is too large (limit is 100 MB unpacked)')
    return zf, lookup


def attach_images(product, names, zf, lookup):
    """Attach the named pictures to a product. Returns a list of warning messages.

    Only products that have NO pictures yet get any. That makes re-importing the same
    file safe: it never piles up duplicate pictures, and it never replaces pictures the
    owner uploaded by hand.
    """
    if product.images.exists():
        return []

    warnings, has_primary = [], False
    for name in names:
        info = lookup.get(name.lower())
        if info is None:
            warnings.append(f'picture "{name}" was not found in the ZIP')
            continue
        if info.file_size > MAX_IMAGE_BYTES:
            warnings.append(f'picture "{name}" is bigger than 5 MB')
            continue

        data = zf.read(info)
        try:
            Image.open(io.BytesIO(data)).verify()          # really a picture, not a renamed file
        except Exception:
            warnings.append(f'picture "{name}" is not a valid image')
            continue

        ProductImage.objects.create(
            product=product,
            image=ContentFile(data, name=os.path.basename(info.filename)),
            is_primary=not has_primary,                    # first valid picture = main picture
        )
        has_primary = True
    return warnings


# ---------------------------------------------------------------- validating one row
def _decimal(value, field, required=False):
    if value == '':
        if required:
            raise ValueError(f'{field} is required')
        return Decimal('0')
    try:
        number = Decimal(value)
    except InvalidOperation:
        raise ValueError(f'{field} must be a number (got "{value}")')
    if number < 0:
        raise ValueError(f'{field} cannot be negative')
    return number


def _int(value, field, default):
    if value == '':
        return default
    try:
        number = int(float(value))          # Excel often gives 20.0
    except ValueError:
        raise ValueError(f'{field} must be a whole number (got "{value}")')
    if number < 0:
        raise ValueError(f'{field} cannot be negative')
    return number


def _split(value):
    return [part.strip() for part in value.split(',') if part.strip()]


def _parse(record):
    """Validate one row. Returns (product_fields, size_names, color_specs)."""
    name = record.get('name', '')
    if not name:
        raise ValueError('name is required')
    if len(name) > 200:
        raise ValueError('name is longer than 200 characters')

    fields = {
        'name': name,
        'description': record.get('description', ''),
        'selling_price': _decimal(record.get('selling_price', ''), 'selling_price', required=True),
        'base_price': _decimal(record.get('base_price', ''), 'base_price'),
        'stock': _int(record.get('stock', ''), 'stock', 0),
        'low_stock_limit': _int(record.get('low_stock_limit', ''), 'low_stock_limit', 5),
        'fabric': record.get('fabric', '')[:100],
    }
    return fields, _split(record.get('sizes', '')), _split(record.get('colors', ''))


# ---------------------------------------------------------------- saving
def import_rows(rows, category, image_pack=None):
    """image_pack is the (zip, lookup) pair from open_image_zip(), or None if no ZIP was uploaded."""
    created = updated = images_added = 0
    errors, warnings = [], []
    zip_missing_noted = False

    for line, record in rows:
        try:
            fields, size_names, color_specs = _parse(record)
            image_names = _split(record.get('images', ''))

            with transaction.atomic():          # one row = all-or-nothing
                product = Product.objects.filter(name__iexact=fields['name'], category=category).first()
                is_new = product is None

                if is_new:
                    product = Product.objects.create(category=category, **fields)
                else:
                    for key, value in fields.items():
                        setattr(product, key, value)
                    product.save()

                # Only touch sizes/colors if the row actually has them
                if size_names:
                    product.sizes.set([Size.objects.get_or_create(name=n)[0] for n in size_names])
                if color_specs:
                    colors = []
                    for spec in color_specs:
                        color_name, _, hex_code = spec.partition(':')
                        color, _ = Color.objects.get_or_create(
                            name=color_name.strip(),
                            defaults={'hex_code': hex_code.strip() or '#cccccc'},
                        )
                        colors.append(color)
                    product.colors.set(colors)

                # Pictures from the ZIP
                if image_names:
                    if image_pack is None:
                        if not zip_missing_noted:
                            warnings.append({'row': None, 'warning':
                                'The file has pictures listed but no images ZIP was uploaded, so no pictures were attached'})
                            zip_missing_noted = True
                    else:
                        before = product.images.count()
                        for message in attach_images(product, image_names, *image_pack):
                            warnings.append({'row': line, 'warning': message})
                        images_added += product.images.count() - before

            created += is_new
            updated += not is_new

        except ValueError as exc:
            errors.append({'row': line, 'error': str(exc)})

    return {
        'created': created,
        'updated': updated,
        'skipped': len(errors),
        'images_added': images_added,
        'errors': errors,
        'warnings': warnings,
    }