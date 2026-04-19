from django.contrib import admin
from .models import Product, Category, Tag, ProductMeta, UserProfile, Feedback
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    can_delete = False

admin.site.unregister(User)
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

class ProductMetaInline(admin.StackedInline):
    model = ProductMeta
    extra = 0

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "price",
        "category",
        "condition",
        "location",
        "available",
        "seller"
    )
    list_filter = (
        "available",
        "condition",
        "location",
        "category",
        "seller"
    )
    search_fields = (
        "title",
        "description",
        "seller__username",
        "seller__email"
    )
    inlines = [ProductMetaInline]

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UserProfile)
admin.site.register(Feedback)
