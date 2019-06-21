from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

app_name = "api"

urlpatterns =  [
    path('home', views.Home, name="home-page"),
    path('register/', views.Register, name="registration-page"),
    path('', views.login_view, name="login"),
    path('logout', views.logout_view),
    path('products', views.products, name='products'),
    path('products/<str:selectedCategory>/', views.products, name='products'),
    path('products/<str:selectedCategory>/<str:selectedBrand>', views.products, name='products'),
    path('products/my-recommended-products', views.productsRecommended, name="productsRecommended"),
    path('productDetail', views.productDetail, name="productDetail"),
    path('productDetail/<int:productId>/', views.productDetail, name="productDetail"),
    path('productDetail/<int:productId>/order', views.addOrder, name="productDetail"),
    path('knn', views.PreInfoKnn, name="disclamer-algoritm-page"),
    path('knn/index', views.TopRecommendation, name="algorithm-page"),
    path('knn/<int:userId>/', views.Knn, name="knn-page"),
    path('orders', views.orderHistory, name="orderhist-page")
]