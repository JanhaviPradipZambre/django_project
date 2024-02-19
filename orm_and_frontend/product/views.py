from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from product.models import Product,CartTable
from django.db.models import Q
from django.contrib import messages
#password = admin@123
# Create your views here.
def register_user(request):
    data={}
    if request.method=="POST":
        uname=request.POST['username']
        upass=request.POST['password']
        uconf_pass=request.POST['password2']
        #implementation validation
        if(uname=='' or upass=='' or uconf_pass==''):
            data['error_msg'] = 'Fields cannot be empty'
            return render(request,'product/register.html',context=data)
        elif(upass != uconf_pass):
            data['error_msg'] = 'Password and confirm password does not matched'
            return render(request,'product/register.html',context=data)
        elif(User.objects.filter(username=uname).exists()):
            data['error_msg'] = uname + ' already exist'
            return render(request,'product/register.html',context=data)
        else:
            user=User.objects.create(username=uname)
            user.set_password(upass)
            user.save()
            customer=CustomerDetails.objects.create(uid=user)
            customer.save()
            # return HttpResponse("Registration done")
            return redirect('/product/login')
    return render(request,'product/register.html')


def login_user(request):
    data={}
    if request.method=="POST":
        uname=request.POST['username']
        upass=request.POST['password']
        if(uname=='' or upass==''):
            data['error_msg']='Fields cant be empty'
            return render(request,'product/login.html',context=data)
        elif(not User.objects.filter(username=uname).exists()):
            data['error_msg']= uname + " user is not registered"
            return render(request,'product/login.html',context=data)
        else:
            user=authenticate(username=uname,password=upass)
            if user is not None:
                login(request,user)
                return redirect('/product/home')
            else:
                data['error_msg']="Wrong Password"
                return render(request,'product/login.html',context=data)
    return render(request,'product/login.html')

def home(request):
    data = {}
    user_authenticated=request.user.is_authenticated
    print(user_authenticated)
    if(user_authenticated):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        data['user_data']=user.username
        return render(request,'product/home.html',context=data)
    else:
        data['user_data']="User"
        return render(request,'product/home.html',context=data)
    
def user_logout(request):
    logout(request)
    return render(request,'product/home.html',{'user_data':'User'})

# view for product table
def index(request):
    data = {}
    fetched_products = Product.objects.filter(is_active=True)
    data['products']=fetched_products
    user_id=request.user.id
    id_specific_cartitems=CartTable.objects.filter(uid=user_id)
    count=id_specific_cartitems.count()
    data['cart_count']=count
    return render(request,'product/index.html',context=data)


def filter_by_category(request,category_value):
    data = {}
    q1 = Q(is_active=True)
    q2 = Q(category=category_value)
    filtered_products=Product.objects.filter(q1 & q2)
    data['products']=filtered_products
    # Product.objects.filter(is_active=True,category=category_value)
    return render(request,'product/index.html',context=data)

def sort_by_price(request,sort_value):
    data={}
    if sort_value=='asc':
        price = 'price'
    else:
        price = '-price'
    sorted_products=Product.objects.filter(is_active=True).order_by(price)
    data['products']=sorted_products
    return render(request,'product/index.html',context=data)
   
def filter_by_rating(request,rating_value):
    data = {}
    q1 = Q(is_active=True)
    q2 = Q(rating__gt=rating_value)
    filtered_products=Product.objects.filter(q1 & q2)
    data['products']=filtered_products
    return render(request,'product/index.html',context=data) 

def filter_by_price_range(request):
    data = {}
    min = request.GET['min']
    max = request.GET['max']
    q1 = Q(price__gte=min)
    q2 = Q(price__lte=max)
    q3 = Q(is_active=True)
    filtered_products=Product.objects.filter(q1 & q2 & q3)
    data['products']=filtered_products
    return render(request,'product/index.html',context=data) 

def product_detail(request,pid):
    product=Product.objects.get(id=pid)
    return render(request,'product/product_detail.html',{'product':product})

def add_to_cart(request,pid):
    if request.user.is_authenticated:
        uid = request.user.id
        print("user id =",uid)
        print("product id =",pid)
        user = User.objects.get(id=uid)
        product = Product.objects.get(id=pid)
        # 
        cart = CartTable.objects.create(pid=product,uid=user)
        cart.save()
        return redirect("/product/index")
    else:
        return redirect("/product/login")
    
def view_cart(request):
    data={}
    user_id=request.user.id
    user=User.objects.get(id=user_id)
    id_specific_cartitems=CartTable.objects.filter(uid=user_id)
    data['products']=id_specific_cartitems
    data['user']=user
    count=id_specific_cartitems.count()
    # data['cart_count']=count
    total_price=0
    total_quantity=0
    for item in id_specific_cartitems:
        total_price=total_price+(item.pid.price*item.quantity)
        total_quantity+=item.quantity
    data['total_price']=total_price
    data['cart_count']=total_quantity
    return render(request, 'product/cart.html',context=data)

def remove_item(request,cartid):
    cart=CartTable.objects.filter(id=cartid)
    cart.delete()
    return redirect('/product/view_cart')

def update_quantity(request,flag,cartid):
    cart=CartTable.objects.filter(id=cartid)
    actual_quantity = cart[0].quantity
    if(flag=="1"):
        cart.update(quantity = actual_quantity+1)
        pass
    else:
        if(actual_quantity>1):
            cart.update(quantity = actual_quantity-1)
            pass
    return redirect('/product/view_cart')


from product.models import OrderTable
def place_order(request):
    data={}
    user_id=request.user.id
    user=User.objects.get(id=user_id)
    id_specific_cartitems=CartTable.objects.filter(uid=user_id)
    customer= CustomerDetails.objects.get(uid = user_id)
    data['customer']=customer
    data['products']=id_specific_cartitems
    data['user']=user
    total_price=0
    total_quantity=0
    for item in id_specific_cartitems:
        total_price=total_price+(item.pid.price*item.quantity)
        total_quantity+=item.quantity
    data['total_price']=total_price
    data['cart_count']=total_quantity
    return render(request, 'product/order.html',context=data)

from product.models import CustomerDetails
def edit_profile(request):
    data={}
    user_id=request.user.id
    customer_querySet=CustomerDetails.objects.filter(uid=user_id)
    customer=customer_querySet[0]
    data['customer']=customer
    if request.method=='POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        phone=request.POST['phone']
        email=request.POST['email']
        address_type=request.POST['address_type']
        full_address=request.POST['full_address']
        pincode=request.POST['pincode']
        print(first_name,last_name,phone,email,address_type,full_address,pincode)
        customer_querySet.update(first_name=first_name,last_name=last_name,phone=phone,email=email,address_type=address_type,full_address=full_address,pincode=pincode)
        return redirect('/product/index')
    return render(request,'product/edit_profile.html',context=data)

import razorpay
def make_payment(request):
    #getting total amount
    user_id=request.user.id
    # user=User.objects.get(id=user_id)
    id_specific_cartitems=CartTable.objects.filter(uid=user_id)
    total_price=0
    for item in id_specific_cartitems:
        total_price=total_price+(item.pid.price*item.quantity)
    data={}    
    client = razorpay.Client(auth=("rzp_test_7dZboVCydQsIy6", "W3xfW92BqaqGFaxfuthsRRZR"))
    data = { "amount": total_price*100, "currency": "INR", "receipt": "order_rcptid_11" }
    # data['amount']=total_price*100
    # data['currency']="INR"
    # data['receipt']="order_rcptid_11"
    payment = client.order.create(data=data)  
    print(payment)
    return render(request,'product/pay.html',context=data)
    

    