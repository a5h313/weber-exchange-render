from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView
from .forms import FeedbackForm, SignUpForm, ProductForm, ProductImageFormSet, EmailLoginForm
from .models import Product, UserProfile, Tag


# Create your views here.
def landing(request: HttpRequest) -> HttpResponse:
    products = Product.objects.all().order_by('postedAt')[:5]
    return render(request, 'landing/home.html', {
        'products': products
    })


class ProductListView(ListView):
    template_name = "landing/product-list.html"
    model = Product
    context_object_name = "products"
    ordering = ["-postedAt"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        favorite_ids = []
        if self.request.user.is_authenticated:
            favorite_ids = list(
                self.request.user.favorite_products.values_list('id', flat=True)
            )

        context["favorite_ids"] = favorite_ids
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    template_name = "landing/product-detail.html"
    model = Product
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        is_favorite = self.object.favorited_by.filter(id=self.request.user.id).exists()
        context["is_favorite"] = is_favorite
        return context



@login_required
def toggle_favorite(request: HttpRequest, product_id: int) -> HttpResponse:
    if request.method != "POST":
        return redirect('product-list')

    product = get_object_or_404(Product, id=product_id)

    if product.favorited_by.filter(id=request.user.id).exists():
        product.favorited_by.remove(request.user)
    else:
        product.favorited_by.add(request.user)

    return redirect('product-detail', slug=product.slug)


def signup_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(
                user=user,
                display_name=form.cleaned_data['display_name'],
            )

            login(request, user, backend='landing.backends.EmailBackend')
            return redirect('my-page')
    else:
        form = SignUpForm()

    return render(request, 'landing/signup.html', {
        'form': form
    })


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('my-page')

    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user, backend='landing.backends.EmailBackend')
                return redirect('my-page')

            form.add_error(None, "Invalid email or password.")
    else:
        form = EmailLoginForm()

    return render(request, 'landing/login.html', {
        'form': form
    })


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        logout(request)
    return redirect('landing')


@login_required
def my_page(request: HttpRequest) -> HttpResponse:
    uploaded_products = request.user.products.all().order_by('-postedAt')
    favorite_products = request.user.favorite_products.all().order_by('-postedAt')
    profile = request.user.profile

    return render(request, 'landing/my-page.html', {
        'profile': profile,
        'uploaded_products': uploaded_products,
        'favorite_products': favorite_products,
    })



@login_required
def product_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.available = True
            product.save()

            existing_tags = form.cleaned_data.get("existing_tags")
            if existing_tags:
                product.tags.add(*existing_tags)

            new_tags = form.cleaned_data.get("new_tags", "")
            if new_tags:
                tag_names = [tag.strip().lower() for tag in new_tags.split(",") if tag.strip()]
                for tag_name in tag_names:
                    tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                    product.tags.add(tag_obj)

            formset.instance = product
            formset.save()

            product_images = product.images.all().order_by("id")
            first_image = product_images.first()

            if first_image:
                product_images.update(is_primary=False)
                first_image.is_primary = True
                first_image.save()

            return redirect("product-detail", slug=product.slug)

    else:
        form = ProductForm()
        formset = ProductImageFormSet()

    return render(request, "landing/product-create.html", {
        "form": form,
        "formset": formset,
    })


def contact(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = FeedbackForm()

    return render(request, 'landing/contact.html', {
        'form': form
    })


def thanks(request: HttpRequest) -> HttpResponse:
    return render(request, 'landing/thanks.html')


def about(request: HttpRequest) -> HttpResponse:
    return render(request, 'landing/about.html')
