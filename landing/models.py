from django.utils import timezone
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.display_name


class ProductMeta(models.Model):
    product = models.OneToOneField(
        "Product",
        on_delete=models.CASCADE,
        related_name='meta',
    )
    views = models.PositiveIntegerField(default=0)
    bumped_at = models.DateTimeField(default=timezone.now)
    is_featured = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Meta for {self.product.title}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super().save(*args, **kwargs)


class Condition(models.TextChoices):
    NEW = 'new', 'New'
    EXCELLENT = 'excellent', 'Excellent'
    GOOD = 'good', 'Good'
    FAIR = 'fair', 'Fair'
    POOR = 'poor', 'Poor'


class Location(models.TextChoices):
    SU = 'shepherd-union', 'Shepherd Union'
    LI = 'steward-library', 'Steward Library'
    NB = 'noorda-building', 'Noorda Building'
    TY = 'tracy-hall', 'Tracy Hall'


class Product(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )
    condition = models.CharField(
        max_length=10,
        choices=Condition.choices,
        default=Condition.GOOD,
    )
    location = models.CharField(
        max_length=20,
        choices=Location.choices,
        default=Location.SU,
    )
    available = models.BooleanField(default=True)
    postedAt = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='products',
    )
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='products',
    )
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='favorite_products',
    )
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return f"{self.title} | ${self.price}"

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"



class Feedback(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    image = models.ImageField(upload_to='images_feedback/', null=True, blank=True)
