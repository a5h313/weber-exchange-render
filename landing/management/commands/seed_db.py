import csv
from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from landing.models import (
    Product,
    ProductMeta,
    Category,
    Condition,
    Location,
)


class Command(BaseCommand):
    help = "Imports data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the csv file")

    @transaction.atomic
    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        User = get_user_model()

        valid_conditions = {c.value for c in Condition}
        valid_locations = {l.value for l in Location}

        required_cols = {
            "title", "price", "category", "condition", "location",
            "available", "seller", "image", "description"
        }

        try:
            with open(file_path, mode="r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)

                if not reader.fieldnames:
                    self.stdout.write(self.style.ERROR("Error: CSV has no header row."))
                    return

                missing = required_cols - set(h.strip() for h in reader.fieldnames)
                if missing:
                    self.stdout.write(self.style.ERROR(
                        f"Error: Missing required column(s): {sorted(missing)}. "
                        f"Found: {reader.fieldnames}"
                    ))
                    return

                for row in reader:
                    row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}

                    title = row.get("title", "").strip()
                    if not title:
                        self.stdout.write(self.style.ERROR("Error: Missing title in a row; skipping."))
                        continue

                    # boolean field handling
                    available_bool = row.get("available", "").strip().lower() == "true"

                    # decimal field handling
                    try:
                        price_decimal = Decimal(row.get("price", "").strip())
                    except (InvalidOperation, AttributeError):
                        self.stdout.write(self.style.ERROR(
                            f"Invalid price for title='{title}'. value='{row.get('price', '')}'"
                        ))
                        continue

                    # condition handling
                    condition_val = row.get("condition", "").strip().lower()
                    if condition_val not in valid_conditions:
                        self.stdout.write(self.style.ERROR(
                            f"Invalid condition for title='{title}'. "
                            f"value='{row.get('condition', '')}'. "
                            f"Expected one of: {sorted(valid_conditions)}"
                        ))
                        continue

                    # location handling
                    location_val = row.get("location", "").strip()
                    if location_val not in valid_locations:
                        self.stdout.write(self.style.ERROR(
                            f"Invalid location for title='{title}'. "
                            f"value='{row.get('location', '')}'. "
                            f"Expected one of: {sorted(valid_locations)}"
                        ))
                        continue

                    # FK: Category
                    category_name = row.get("category", "").strip()
                    if not category_name:
                        self.stdout.write(self.style.ERROR(f"Error: Missing category for title='{title}'; skipping."))
                        continue
                    category_obj, _ = Category.objects.get_or_create(name=category_name)

                    # FK: Seller (User)
                    seller_username = row.get("seller", "").strip()
                    if not seller_username:
                        self.stdout.write(self.style.ERROR(f"Error: Missing seller for title='{title}'; skipping."))
                        continue
                    seller_obj, _ = User.objects.get_or_create(username=seller_username)

                    obj, created = Product.objects.get_or_create(
                        title=title,
                        defaults={
                            "price": price_decimal,
                            "category": category_obj,
                            "condition": condition_val,
                            "location": location_val,
                            "available": available_bool,
                            "seller": seller_obj,
                            "image": row.get("image", "").strip(),
                            "description": row.get("description", "").strip() or None,
                        }
                    )

                    # Ensure 1:1 meta exists
                    ProductMeta.objects.get_or_create(product=obj)

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Imported: {title}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Skipped: {title}"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: File not found: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))