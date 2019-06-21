from django.contrib import admin
from .models import User, Author, Product, ProductList, Order
# Register your models here.
CustomUser = User
admin.site.register(CustomUser)
 

# Register your models here.
#Maakt het mogelijk om bij het admin paneel deze dingen te wijzigen.
admin.site.register(Author)                 
admin.site.register(Product)
admin.site.register(ProductList)
admin.site.register(Order)