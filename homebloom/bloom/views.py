from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,get_user_model,logout
from .forms import SignupForm, LoginForm,ForgotPasswordForm, OTPVerifyForm, ResetPasswordForm
from .models import PasswordResetOTP, Product, Category,SubCategory,Banner,Wishlist
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from decimal import Decimal, InvalidOperation
import random
from django.db.models.functions import Coalesce


User = get_user_model()

@never_cache
def home(request):
    banners = Banner.objects.filter(page='home',is_active=True)
    whats_new_products = Product.objects.filter(is_new=True,is_active=True).order_by("-created_at")[:6]
    best_sellers = Product.objects.filter(is_best_seller=True,is_active=True).order_by("-created_at")[:8]

    return render(request, "home.html", {
        "banners": banners,
        "whats_new_products": whats_new_products,
        "best_sellers": best_sellers,
    })
    
    
@never_cache
def furniture(request):
    banner = Banner.objects.filter(page="furniture", is_active=True).first()
    products = Product.objects.filter(category__name__iexact="Furniture",is_active=True)
    sub_id = request.GET.get("sub_id")

    if sub_id:
        products = products.filter(subcategory_id=sub_id)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    try:
        min_price = int(min_price) if min_price else None
    except ValueError:
        min_price = None

    try:
        max_price = int(max_price) if max_price else None
    except ValueError:
        max_price = None

    if min_price is not None:
        products = products.filter(price__gte=min_price)

    if max_price is not None:
        products = products.filter(price__lte=max_price)

    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True))

    return render(request, "furniture.html", {
        "banner": banner,
        "products": products,
        "selected_sub_id": sub_id,
        "min_price": min_price,
        "max_price": max_price,
        "wishlist_products": wishlist_products,
    })

    
@never_cache
def walldecor(request):
    
    banner = Banner.objects.filter(page="walldecor", is_active=True).first()

    products = Product.objects.filter(
        category__name__iexact="Wall Decor",
        is_active=True
    )

    sub_id = request.GET.get("sub_id")
    if sub_id:
        products = products.filter(subcategory_id=sub_id)

    min_price_raw = request.GET.get("min_price")
    max_price_raw = request.GET.get("max_price")

    try:
        min_price = Decimal(min_price_raw) if min_price_raw else None
    except InvalidOperation:
        min_price = None

    try:
        max_price = Decimal(max_price_raw) if max_price_raw else None
    except InvalidOperation:
        max_price = None
        
    products = products.annotate(
        effective_price=Coalesce("offer_price", "price")
    )

    if min_price is not None:
        products = products.filter(price__gte=min_price)

    if max_price is not None:
        products = products.filter(price__lte=max_price)
        
    return render(request, "walldecor.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
    })

    
@never_cache
def kitchen(request):
    

    banner = Banner.objects.filter(page="kitchen", is_active=True).first()

    products = Product.objects.filter(
        category__name__iexact="Kitchen & Dining",
        is_active=True
    )

    sub_id = request.GET.get("sub_id")
    if sub_id:
        products = products.filter(subcategory_id=sub_id)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    try:
        min_price = Decimal(min_price) if min_price else None
    except InvalidOperation:
        min_price = None

    try:
        max_price = Decimal(max_price) if max_price else None
    except InvalidOperation:
        max_price = None

    if min_price is not None and max_price is not None:
        if min_price > max_price:
            min_price, max_price = max_price, min_price

    if min_price is not None:
        products = products.filter(price__gte=min_price)

    if max_price is not None:
        products = products.filter(price__lte=max_price)

    return render(request, "kitchen.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
    })
    
@never_cache
def lighting(request):
    banner = Banner.objects.filter(page="lighting", is_active=True).first()

    products = Product.objects.filter(
        category__name__iexact="Lighting",
        is_active=True
    )

    sub_id = request.GET.get("sub_id")
    if sub_id:
        products = products.filter(subcategory_id=sub_id)

    min_price_raw = request.GET.get("min_price")
    max_price_raw = request.GET.get("max_price")

    try:
        min_price = Decimal(min_price_raw) if min_price_raw else None
    except InvalidOperation:
        min_price = None

    try:
        max_price = Decimal(max_price_raw) if max_price_raw else None
    except InvalidOperation:
        max_price = None
        
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            min_price, max_price = max_price, min_price

    if min_price is not None:
        products = products.filter(price__gte=min_price)

    if max_price is not None:
        products = products.filter(price__lte=max_price)

    return render(request, "lighting.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
    })
@never_cache
def bath(request):
    banner = Banner.objects.filter(page="bath", is_active=True).first()

    products = Product.objects.filter(category__name__iexact="Accessories",is_active=True)

    sub_id = request.GET.get("sub_id")
    if sub_id:
        products = products.filter(subcategory_id=sub_id)

    min_price_raw = request.GET.get("min_price")
    max_price_raw = request.GET.get("max_price")

    try:
        min_price = Decimal(min_price_raw) if min_price_raw else None
    except InvalidOperation:
        min_price = None

    try:
        max_price = Decimal(max_price_raw) if max_price_raw else None
    except InvalidOperation:
        max_price = None
        
    if min_price is not None and max_price is not None:
        if min_price > max_price:
            min_price, max_price = max_price, min_price

    if min_price is not None:
        products = products.filter(price__gte=min_price)

    if max_price is not None:
        products = products.filter(price__lte=max_price)

    return render(request, "bath.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
    })
    
    
@never_cache
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")

    return render(request, "signup.html", {"form": form})

@never_cache
def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        
        if user.is_active:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect("/")
        else:
            return render(request, "login.html", {"form": form})

    return render(request, "login.html", {"form": form})


@never_cache
def forgot(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()

            if not user:
                messages.error(request, "No account found with this email")
                return render(request, "forgot.html", {"form": form})

            otp = str(random.randint(100000, 999999))

            PasswordResetOTP.objects.filter(user=user).delete()
            PasswordResetOTP.objects.create(user=user, otp=otp)

            try:
                send_mail(
                    "Password Reset OTP",
                    f"Your OTP is {otp}. It expires in 5 minutes.",
                    None,
                    [email],
                )
            except Exception as e:
                messages.error(request, "Failed to send OTP email")
                return render(request, "forgot.html", {"form": form})

            request.session["reset_user"] = user.id
            return redirect("verify_otp")

        else:
            print(form.errors)

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

def addaddress(request):
    return render(request,'addaddress.html')

@login_required(login_url='login')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
    else:
        # not in wishlist → add
        Wishlist.objects.create(
            user=request.user,
            product=product
        )
    return redirect(request.META.get('HTTP_REFERER', '/'))

@never_cache
@login_required(login_url="login")
def cart(request):
    return render(request,'cart.html')
@never_cache
@login_required(login_url="login")
def checkout(request):
    return render(request,'checkout.html')
def faq(request):
    return render(request,'faq.html')
def privacy(request):
    return render(request,'privacy.html')
def aboutus(request):
    return render(request,'aboutus.html')


@never_cache
@login_required(login_url="login")
def product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    related_products = Product.objects.filter(category=product.category,is_active=True).exclude(id=product.id)[:4]

    return render(request, "product.html", {
        "product": product,
        "related_products": related_products,
    })



@never_cache
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


@never_cache
@login_required
def admindashboard(request):
    total_products = Product.objects.count()

    context = {
        "total_products": total_products,
    }

    return render(request, "admindashboard.html", context)

@never_cache
def adminproduct(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, "adminproduct.html", {
        "products": products
    })
    
    
@never_cache    
def productedit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        selected_category_id = request.POST.get("category")

        if "submit_product" in request.POST:
            product.name = request.POST.get("name")
            product.category_id = selected_category_id
            product.subcategory_id = request.POST.get("subcategory")
            product.price = request.POST.get("price")
            offer_price = request.POST.get("offer_price")
            product.offer_price = offer_price if offer_price else None
            product.quantity = request.POST.get("quantity")
            product.description = request.POST.get("description")
            
            product.is_new = "is_new" in request.POST
            product.is_best_seller = "is_best_seller" in request.POST

            for i in range(1, 5):
                img = request.FILES.get(f"image{i}")
                if img:
                    setattr(product, f"image{i}", img)

            product.save()
            return redirect("adminproduct")

    else:
        selected_category_id = product.category_id

    subcategories = SubCategory.objects.filter(category_id=selected_category_id)

    return render(request, "productedit.html", {
        "product": product,
        "categories": categories,
        "subcategories": subcategories,
        "selected_category_id": int(selected_category_id) if selected_category_id else None,
    })


def product_toggle_status(request, id):
    product = get_object_or_404(Product, id=id)
    product.is_active = not product.is_active
    product.save()
    return redirect('adminproduct')


@never_cache
@login_required(login_url="login")

def admincustomer(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    customers = User.objects.filter(is_staff=False)

    return render(request, "admincustomer.html", {
        "customers": customers
    })
    
@login_required(login_url="login")
@never_cache
def toggle_customer_block(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    user = get_object_or_404(User, id=user_id, is_staff=False)

    user.is_active = not user.is_active
    user.save()

    return redirect("admincustomer")
    
@never_cache
@login_required(login_url="login")
def delete_customer(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")
    user = get_object_or_404(User, id=user_id, is_staff=False)

    if request.method == "POST":
        user.delete()
        return redirect("admincustomer") 
    
    
@never_cache
@login_required(login_url="login")  
def admincategory(request):
    categories = Category.objects.all()

    return render(request, "admincategory.html", {
        "categories": categories
    })
    
@never_cache
@login_required(login_url="login")   
def categoryedit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    subcategories = SubCategory.objects.filter(category=category)

    if request.method == "POST":

        delete_sub_id = request.POST.get("delete_sub")
        if delete_sub_id:
            SubCategory.objects.filter(
                id=delete_sub_id,
                category=category
            ).delete()
            messages.success(request, "Subcategory deleted successfully.")
            return redirect("categoryedit", pk=pk)

        category.name = request.POST.get("category_name")
        category.save()

        for sub in subcategories:
            new_name = request.POST.get(f"sub_{sub.id}")
            if new_name:
                sub.name = new_name
                sub.save()

        new_sub = request.POST.get("new_subcategory")
        if new_sub:
            SubCategory.objects.create(
                name=new_sub,
                category=category
            )

        messages.success(request, "Category updated successfully.")
        return redirect("admincategory")

    return render(request, "categoryedit.html", {
        "category": category,
        "subcategories": subcategories
    })

@never_cache
@login_required(login_url="login")
def categoryadd(request):
    if request.method == "POST" and "delete_category" in request.POST:
        cat_id = request.POST.get("delete_category")
        Category.objects.filter(id=cat_id).delete()
        return redirect("categoryadd")

    if request.method == "POST" and "edit_category" in request.POST:
        cat_id = request.POST.get("edit_category")
        new_name = request.POST.get("edit_name")

        if new_name:
            Category.objects.filter(id=cat_id).update(name=new_name)

        return redirect("categoryadd")
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            return redirect("admincategory")

    categories = Category.objects.all()

    return render(request, "categoryadd.html", {
        "categories": categories
    })

@never_cache
@login_required(login_url="login")
def categorydelete(request, pk):
    if request.method == "POST":
        category = get_object_or_404(Category, pk=pk)

        # Optional safety check
        if category.subcategory_set.exists() or category.product_set.exists():
            # You can add messages framework later
            return redirect("admincategory")

        category.delete()

    return redirect("admincategory")


@never_cache
def admincoupon(request):
    return render(request,'admincoupon.html')

@never_cache
def couponedit(request):
    return render(request,'couponedit.html')

@never_cache
def adminorder(request):
    return render(request,'adminorder.html')

@never_cache
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
    

@never_cache
def adminlogout(request):
    logout(request)
    return redirect("home")

@never_cache
def userlogout(request):
    logout(request)
    return redirect("login")

@never_cache
@login_required(login_url="adminpanel")
def banner_add(request):
    if request.method == "POST":
        if request.POST.get("delete_banner_id"):
            banner = Banner.objects.get(id=request.POST.get("delete_banner_id"))
            banner.delete()
            return redirect("banner_add")
        
        Banner.objects.create(
            title=request.POST.get("title"),
            subtitle=request.POST.get("subtitle"),
            page=request.POST.get("page"),
            image=request.FILES.get("image"),
        )
        return redirect("banner_add")

    banners = Banner.objects.all()
    return render(request, "adminbanner.html", {
        "banners": banners
    })
    
@never_cache
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, is_active=True)
    return render(request, "product.html", {
        "product": product
    })  
    
def search(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=query) |
            Q(subcategory__name__icontains=query)
        ).distinct()

    return render(request, "search.html", {
        "products": products,
        "query": query
    })


    
    
    
    
    
    
    
    
    
    
    
    
    
    