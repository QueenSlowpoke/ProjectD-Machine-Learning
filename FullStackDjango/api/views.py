from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse, HttpResponseRedirect
from api.forms import RegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_user_model, login, logout
from .Recommender import Recommender

from django.http import HttpRequest
from django.template import RequestContext
from .models import User, Product, Order, ProductList
from rest_framework.response import Response
from rest_framework.views import APIView
# from .serializers import ArticleSerializer
# Create your views here.


def PreInfoKnn(request):
    return render(request, 'algorithmDisclaimer.html')

# this path is for entering the algorithm view. however no user is selected therefore it returns top 10 recommend items
def TopRecommendation(request):
    dev = User.objects.all().filter(jobtitle = "Developer")      
    des = User.objects.all().filter(jobtitle = "Designer")
    off = User.objects.all().filter(jobtitle = "Office")
    test = Recommender(5)
    products = test.GetTopBorrowedItems(10)
    print(products)
        
    return render(request, 'topItem.html', {'products': products, 'developers': dev, 'designers': des, 'office': off})

def Knn(request, userId):
    #get selected user information 
    query = connection.cursor().execute("SELECT * FROM api_user WHERE id =" + str(userId))
    currentUser = query.fetchall()

    #Get UserHistory
    recommender = Recommender(userId)
    hist, haveHist = recommender.CheckAndGetHistory()
    recommendList = recommender.Knn(hist)

    print(currentUser)
    dev = User.objects.all().filter(jobtitle = "Developer")      
    des = User.objects.all().filter(jobtitle = "Designer")
    off = User.objects.all().filter(jobtitle = "Office") #required for side menu
    return render(request, 'knn.html', {'developers': dev, 'designers': des, 'office': off, 'currentUser': currentUser, 'history': haveHist, 'recommend': recommendList})

@login_required(login_url='/')
def Home(request):
    id = request.user.id
    query = connection.cursor().execute("SELECT * FROM api_user WHERE id =" + str(id))
    currentUser = query.fetchall()
    print()

    #Get UserHistory
    recommender = Recommender(id)
    hist, haveHist = recommender.CheckAndGetHistory()
    recommendList = recommender.Knn(hist)
    #Gooit het resultaat van Id's in een lijst en pakt alle producten met die Id's. 
    idList = []
    Recommended = []
    for item in recommendList:
        idList.append(item[0])
    for item in idList:
        query = connection.cursor().execute("SELECT * FROM api_product WHERE id =" + str(item))
        product = query.fetchall()
        Recommended.append(product)


    return render(request, "home.html", {'product' : Recommended})

def Register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/home')
    else:
        form = RegistrationForm()   
    return render(request, 'register.html', {'form': form})

def login_view(request):
    next = request.GET.get('next')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('/home')
    return render(request, "login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')



## Webpagina die Db info laat zien ##
@login_required(login_url='/')
def products(request, selectedCategory, selectedBrand):
    if selectedCategory == '0':
        Product_list = Product.objects.all() ## Product List = Variabel, Objects.all() pakt alle producten in de DB ##
    elif selectedBrand == '0': 
        query = connection.cursor().execute("SELECT * FROM api_product WHERE category = '" + str(selectedCategory) + "'")
        Product_list = query.fetchall()
    else:
        query = connection.cursor().execute("SELECT * FROM api_product WHERE category = '" + str(selectedCategory) + "' AND brand = '" + str(selectedBrand) + "'")
        Product_list = query.fetchall()

       


    page = request.GET.get('page', 1)
    paginator = Paginator(Product_list, 10)
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)

    
    query = connection.cursor().execute("SELECT category FROM api_product GROUP BY category")
    categories = query.fetchall()

    if selectedCategory != '0':
          query = connection.cursor().execute("SELECT brand FROM api_product WHERE category = '" + str(selectedCategory) + "'GROUP BY brand")
          brands = query.fetchall()  
    
    if selectedCategory == '0':
        return render(request, 'api/products.html', {'Product': product, 'Categories': categories, 'enabledCategories': False}) 
    else:
        return render(request, 'api/products.html', {'Product': product, 'Categories': categories, 'enabledCategories': True, 'currentCategorie': str(selectedCategory), 'Brands': brands}) 
    

@login_required(login_url='/')
def productsRecommended(request):
    #get selected user information 
    id = request.user.id
    query = connection.cursor().execute("SELECT * FROM api_user WHERE id =" + str(id))
    currentUser = query.fetchall()
    print()

    #Get UserHistory
    recommender = Recommender(id)
    hist, haveHist = recommender.CheckAndGetHistory()
    recommendList = recommender.Knn(hist)
    #Gooit het resultaat van Id's in een lijst en pakt alle producten met die Id's. 
    idList = []
    Recommended = []
    for item in recommendList:
        idList.append(item[0])
    for item in idList:
        query = connection.cursor().execute("SELECT * FROM api_product WHERE id =" + str(item))
        product = query.fetchall()
        Recommended.append(product)


    return render(request, 'api/products.html', {'Product': Recommended, 'Recommended': True})

@login_required(login_url='/')
def productDetail(request, productId):
        query = connection.cursor().execute("SELECT * FROM api_product WHERE id =" + str(productId))
        product = query.fetchall()
        return render(request, 'api/detailPage.html',{'Product': product})

@login_required(login_url='/')
def orderHistory(request):
    id = request.user.id
    print(id)
    orderHistory = []
    query = connection.cursor().execute("SELECT api_order.id, api_productlist.product_id, api_product.title, api_product.image, api_product.id, api_productlist.amount, api_product.category FROM api_order JOIN api_productlist ON api_order.id = api_productlist.order_id JOIN api_product ON api_productlist.product_id == api_product.id WHERE user_id =" + str(id) + " ORDER BY api_order.id DESC")
    orderList = query.fetchall()
    print(orderList)
    
    userQuery = connection.cursor().execute("SELECT * FROM api_user Where id = " + str(id)) 
    user = userQuery.fetchall()
    page = request.GET.get('page', 1)
    paginator = Paginator(orderList, 10)
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)


    return render(request, 'api/orderHistoryPage.html', {'OrderHistory': product, 'User': user })


@login_required(login_url='/')
def addOrder(request, productId):
    id = request.user.id
    print("This is product ID: " + str(productId))
    query = connection.cursor().execute("select * from api_product where id =" + str(productId))
    Found = query.fetchall()
   
    newOrder = Order.objects.create(user = request.user)
    
    myorder = Order.objects.latest('id')
    myorderId = myorder

    productInstance = Product.objects.get(title = str(Found[0][1]))
    
    addProduct = ProductList.objects.create(product = productInstance , order = myorderId, amount = 1 )

    return render(request, 'api/detailPageOrder.html',{'Product': Found, 'Order': myorderId.id})

