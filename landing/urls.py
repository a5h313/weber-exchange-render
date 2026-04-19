from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-page/', views.my_page, name='my-page'),

    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/create/', views.product_create, name='product-create'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('products/favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),

    path('contact/', views.contact, name='contact'),
    path('thanks/', views.thanks, name='thanks'),
    path('about/', views.about, name='about'),
]