from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,get_user_model
from .forms import SignupForm, LoginForm,ForgotPasswordForm, OTPVerifyForm, ResetPasswordForm,ProductForm
from .models import PasswordResetOTP, Product, Category,SubCategory
from django.core.mail import send_mail
from django.contrib import messages
import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from decimal import Decimal




User = get_user_model()
def home(request):
    return render(request,'home.html')
def furniture(request):
    return render(request,'furniture.html')
def walldecor(request):
    return render(request,'walldecor.html')
def kitchen(request):
    return render(request,'kitchen.html')
def lighting(request):
    return render(request,'lighting.html')
def bath(request):
    return render(request,'bath.html')
from django.contrib.auth import login

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")

    return render(request, "signup.html", {"form": form})


def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("/")

    return render(request, "login.html", {"form": form})


def forgot(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            otp = str(random.randint(100000, 999999))

            PasswordResetOTP.objects.filter(user=user).delete()
            PasswordResetOTP.objects.create(user=user, otp=otp)

            send_mail(
                "Password Reset OTP",
                f"Your OTP is {otp}. It expires in 5 minutes.",
                None,
                [email],
            )

            request.session["reset_user"] = user.id
            return redirect("verify_otp")

    return render(request, "forgot.html", {"form": form})

def verify_otp(request):
    form = OTPVerifyForm(request.POST or None)
    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("forgot")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("forgot")

    otp_obj = PasswordResetOTP.objects.filter(user=user).last()

    if request.method == "POST":
        if "resend" in request.POST:
            if otp_obj:
                otp_obj.delete()

            new_otp = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=user, otp=new_otp)

            send_mail(
                "New OTP",
                f"Your new OTP is {new_otp}",
                None,
                [user.email],
            )
            return redirect("verify_otp")

        if form.is_valid():
            if otp_obj and not otp_obj.is_expired() and form.cleaned_data["otp"] == otp_obj.otp:
                request.session["reset_user_id"] = user.id
                return redirect("reset_password")

    return render(request, "verify_otp.html", {"form": form})


def reset_password(request):
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot")

    user = User.objects.filter(id=user_id).first()
    if not user:
        return redirect("forgot")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST, user=user)
        if form.is_valid():
            form.save()
            del request.session["reset_user_id"]
            return redirect("login")
    else:
        form = ResetPasswordForm(user=user)

    return render(request, "reset_password.html", {"form": form})


def password_changed(request):
    return render(request, "password_changed.html")

@login_required(login_url='login')
def profile(request):
    return render(request,'profile.html')

@login_required(login_url='login')
def order(request):
    return render(request,'order.html')


def detail(reqeust):
    return render(reqeust,'detail.html')
def adminorder(request):
    return render(request,'adminorder.html')
def addaddress(request):
    return render(request,'addaddress.html')

@login_required(login_url='login')
def wishlist(request):
    return render(request,'wishlist.html')


def cart(request):
    return render(request,'cart.html')
def checkout(request):
    return render(request,'checkout.html')
def faq(request):
    return render(request,'faq.html')
def privacy(request):
    return render(request,'privacy.html')
def aboutus(request):
    return render(request,'aboutus.html')
def product(request):
    return render(request,'product.html')

def adminpanel(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username, is_staff=True)
        except User.DoesNotExist:
            messages.error(request, "Invalid admin credentials")
            return render(request, "adminpanel.html")

        if user.check_password(password):
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect("admindashboard")
        else:
            messages.error(request, "Invalid admin credentials")

    return render(request, "adminpanel.html")   
@login_required
def admindashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    return render(request, "admindashboard.html")

def adminproduct(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    
    return render(request, "adminproduct.html", {
        "products": products
    })
    
def productedit(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect("adminproduct")

    categories = Category.objects.all()
    

    selected_category_id = request.POST.get("category")
    if selected_category_id:
        selected_category_id = str(selected_category_id)
    else:
        selected_category_id = str(product.category_id) if product.category_id else None
    
    subcategories = SubCategory.objects.filter(
        category_id=selected_category_id
    ) if selected_category_id else SubCategory.objects.none()

    if request.method == "POST":
        if "submit_product" not in request.POST:
            return render(request, "productedit.html", {
                "product": product,
                "categories": categories,
                "subcategories": subcategories,
                "selected_category_id": selected_category_id,
            })
        
       
        name = request.POST.get("name", "").strip()
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        
        if not all([name, category_id, subcategory_id, price, quantity]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, "productedit.html", {
                "product": product,
                "categories": categories,
                "subcategories": subcategories,
                "selected_category_id": selected_category_id,
            })
        
        try:
            
            product.name = name
            product.category_id = category_id
            product.subcategory_id = subcategory_id
            product.price = float(price)
            product.quantity = int(quantity)
            product.description = request.POST.get("description", "").strip()
            
            offer_price = request.POST.get("offer_price", "").strip()
            product.offer_price = float(offer_price) if offer_price else None
            
            offer = request.POST.get("offer", "").strip()
            product.offer = float(offer) if offer else None

            for i in range(1, 5):
                image_field = f"image{i}"
                if request.FILES.get(image_field):
                    setattr(product, image_field, request.FILES.get(image_field))
            
            product.save()
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect("adminproduct")
            
        except (ValueError, TypeError) as e:
            messages.error(request, "Invalid data provided. Please check your inputs.")
            return render(request, "productedit.html", {
                "product": product,
                "categories": categories,
                "subcategories": subcategories,
                "selected_category_id": selected_category_id,
            })
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return render(request, "productedit.html", {
                "product": product,
                "categories": categories,
                "subcategories": subcategories,
                "selected_category_id": selected_category_id,
            })

    return render(request, "productedit.html", {
        "product": product,
        "categories": categories,
        "subcategories": subcategories,
        "selected_category_id": selected_category_id,
    })

def product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('adminproduct')

@login_required
def admincustomer(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    customers = User.objects.filter(is_staff=False)

    return render(request, "admincustomer.html", {
        "customers": customers
    })
    
@login_required
def delete_customer(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")
    user = get_object_or_404(User, id=user_id, is_staff=False)

    if request.method == "POST":
        user.delete()
        return redirect("admincustomer") 
    
def admincategory(request):
    return render(request,'admincategory.html')
def categoryedit(request):
    return render (request,'categoryedit.html')

def category_add(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Category name is required.")
            return redirect("categoryadd")

        Category.objects.create(
            name=name,
            description=description
        )
        messages.success(request, "Category added successfully.")
        return redirect("admincategory")

    return render(request, "categoryadd.html")


def admincoupon(request):
    return render(request,'admincoupon.html')
def couponedit(request):
    return render(request,'couponedit.html')
def chairs(request):
    return render(request,'chairs.html')

from decimal import Decimal
from .models import Category, SubCategory, Product

def add_product(request):
    categories = Category.objects.all()

    selected_category_id = request.POST.get("category")
    subcategories = SubCategory.objects.filter(
        category_id=selected_category_id
    ) if selected_category_id else []

    if request.method == "POST" and "submit_product" in request.POST:
        Product.objects.create(
            name=request.POST.get("name"),
            category_id=selected_category_id,
            subcategory_id=request.POST.get("subcategory"),
            price=Decimal(request.POST.get("price")),
            offer_price=request.POST.get("offer_price") or None,
            quantity=int(request.POST.get("quantity")),
            offer=request.POST.get("offer") or None,
            description=request.POST.get("description", ""),
            image1=request.FILES.get("image1"),
            image2=request.FILES.get("image2"),
            image3=request.FILES.get("image3"),
            image4=request.FILES.get("image4"),
        )
        return redirect("adminproduct")

    return render(request, "addproduct.html", {
        "categories": categories,
        "subcategories": subcategories,
        "selected_category_id": selected_category_id,
        "form_data": request.POST,
    })

