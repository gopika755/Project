from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login,get_user_model,logout
from .forms import SignupForm, LoginForm,ForgotPasswordForm, OTPVerifyForm, ResetPasswordForm,AddressForm
from .models import PasswordResetOTP, Product, Category,SubCategory,Banner,Wishlist,Cart,Profile,Address,Order,OrderItem
from django.core.mail import send_mail
from django.db.models import Q,Sum
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.http import HttpResponseForbidden,JsonResponse
from decimal import Decimal, InvalidOperation
import random,stripe
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()

from django.views.decorators.cache import never_cache
from django.db.models import Sum
from .models import Cart, Banner, Product


@never_cache
def home(request):
    banners = Banner.objects.filter(page='home', is_active=True)
    whats_new_products = Product.objects.filter(is_new=True, is_active=True).order_by("-created_at")[:6]
    best_sellers = Product.objects.filter(is_best_seller=True, is_active=True).order_by("-created_at")[:8]

    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user)\
            .aggregate(total=Sum("quantity"))["total"] or 0
    else:
        cart_count = 0

    return render(request, "home.html", {
        "banners": banners,
        "whats_new_products": whats_new_products,
        "best_sellers": best_sellers,
        "cart_count": cart_count, 
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
        
    cart_product_ids = []
    if request.user.is_authenticated:
        cart_product_ids = list(Cart.objects.filter(user=request.user).values_list("product_id", flat=True))

    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user)\
            .aggregate(total=Sum("quantity"))["total"] or 0
    else:
        cart_count = 0
        
    return render(request, "furniture.html", {
        "banner": banner,
        "products": products,
        "selected_sub_id": sub_id,
        "min_price": min_price,
        "max_price": max_price,
        "wishlist_products": wishlist_products,
        "cart_product_ids":cart_product_ids,
        "cart_count": cart_count,
    })

    
@never_cache
def walldecor(request):
    banner = Banner.objects.filter(page="walldecor", is_active=True).first()
    products = Product.objects.filter(category__name__iexact="Wall Decor",is_active=True)

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
        products = products.filter(effective_price__gte=min_price)

    if max_price is not None:
        products = products.filter(effective_price__lte=max_price)
        
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True))
    
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user)\
            .aggregate(total=Sum("quantity"))["total"] or 0
    else:
        cart_count = 0
    
    return render(request, "walldecor.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
        "wishlist_products":wishlist_products,
        "cart_count": cart_count,
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

    products = products.annotate(
        effective_price=Coalesce("offer_price", "price")
    )

    if min_price is not None:
        products = products.filter(effective_price__gte=min_price)

    if max_price is not None:
        products = products.filter(effective_price__lte=max_price)
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True))
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user)\
            .aggregate(total=Sum("quantity"))["total"] or 0
    else:
        cart_count = 0
    
        
    return render(request, "kitchen.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
        "wishlist_products":wishlist_products,
        "cart_count": cart_count,
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

    products = products.annotate(
        effective_price=Coalesce("offer_price", "price")
    )

    if min_price is not None:
        products = products.filter(effective_price__gte=min_price)

    if max_price is not None:
        products = products.filter(effective_price__lte=max_price)
        
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True))
    
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user)\
            .aggregate(total=Sum("quantity"))["total"] or 0
    else:
        cart_count = 0
        
    return render(request, "lighting.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
        "wishlist_products":wishlist_products,
        "cart_count": cart_count,
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

    products = products.annotate(
        effective_price=Coalesce("offer_price", "price")
    )

    if min_price is not None:
        products = products.filter(effective_price__gte=min_price)

    if max_price is not None:
        products = products.filter(effective_price__lte=max_price)
        
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_products = list(Wishlist.objects.filter(user=request.user).values_list("product_id", flat=True)) 
    
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user)\
            .aggregate(total=Sum("quantity"))["total"] or 0
    else:
        cart_count = 0
    
        
    return render(request, "bath.html", {
        "banner": banner,
        "products": products,
        "min_price": min_price,
        "max_price": max_price,
        "selected_sub_id": sub_id,
        "wishlist_products":wishlist_products,
        "cart_count": cart_count,
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
        login(request, user)

        if user.is_staff:
            return redirect("admindashboard")
        return redirect("home")

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

@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    addresses = Address.objects.filter(user=request.user).order_by('-id')

    return render(request, "profile.html", {
        "profile": profile,
        "addresses": addresses
    })

    
@login_required
def editprofile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        request.user.first_name = request.POST.get("name")
        request.user.email = request.POST.get("email")
        request.user.save()

        profile.phone = request.POST.get("phone")

        if request.FILES.get("profile_image"):
            profile.image = request.FILES["profile_image"]

        profile.save()
        return redirect("profile")

    return render(request, "editprofile.html", {
        "profile": profile
    })

    
@login_required
def editaddress(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = AddressForm(instance=address)

    return render(request, "editaddress.html", {
        "form": form,
        "address": address
    })


@login_required
def order(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "order.html", {"orders": orders})



@login_required
@staff_member_required
def detail(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, "detail.html", {"order": order})

@login_required
@staff_member_required(login_url="home")
def download_invoice(request, id):
    order = Order.objects.prefetch_related("items__product").get(
        id=id,
        user=request.user
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'



    p = canvas.Canvas(response, pagesize=A4)
    y = 800

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "HOME BLOOM - INVOICE")
    y -= 40

    p.setFont("Helvetica", 10)
    y -= 20
    p.drawString(50, y, f"Date: {order.created_at.strftime('%d %b %Y')}")
    y -= 30

    for item in order.items.all():
        p.drawString(50, y, f"{item.product.name} x {item.quantity}")
        p.drawRightString(550, y, f"₹ {item.price}")
        y -= 20

    y -= 10
    p.drawString(50, y, "-" * 80)
    y -= 20

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Total")
    p.drawRightString(550, y, f"₹ {order.total}")

    p.showPage()
    p.save()

    return response

@never_cache
@staff_member_required(login_url='home')
def addaddress(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST)


        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect("profile")
    else:
        form = AddressForm()

    return render(request, "addaddress.html", {
        "form": form,
        "profile": profile
    })
    
@never_cache
@staff_member_required(login_url='home')
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        address.delete()
        return redirect("profile")


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })
@login_required
@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
        return JsonResponse({"status": "removed"})
    else:
        Wishlist.objects.create(user=request.user, product=product)
        return JsonResponse({"status": "added"})


@login_required
def move_to_cart(request, wishlist_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        id=wishlist_id,
        user=request.user
    )

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=wishlist_item.product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    wishlist_item.delete()
    return redirect('wishlist')


@login_required
def payment_page(request):
    buy_now_product_id = request.session.get("buy_now_product_id")

    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)

        cart_items = [{
            "product": product,
            "quantity": 1,
            "subtotal": product.offer_price or product.price,
        }]

        total = product.offer_price or product.price

        return render(request, "payment.html", {
            "cart_items": cart_items,
            "total": total,
            "buy_now": True,
        })

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("cart")

    total = sum(
        (item.product.offer_price or item.product.price) * item.quantity
        for item in cart_items
    )

    return render(request, "payment.html", {
        "cart_items": cart_items,
        "total": total,
        "buy_now": False,
    })

@login_required
def payment_failed(request):
    order_id = request.GET.get("order_id")

    if order_id:
        from .models import Order
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.payment_status = "FAILED"
            order.save()
        except Order.DoesNotExist:
            pass

    return render(request, "payment_failed.html")

@never_cache
@login_required
def cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect(request.META.get("HTTP_REFERER", "cart"))

    cart_items = Cart.objects.filter(user=request.user)
    subtotal = sum(item.subtotal for item in cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
    })
    
@login_required
def remove_cart_item(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect("cart")

@require_POST
def update_cart_quantity(request):
    cart_id = request.POST.get("cart_id")
    action = request.POST.get("action")

    cart_item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    if action == "increase":
        cart_item.quantity += 1

    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1

    cart_item.save()

    return JsonResponse({
        "status": "success",
        "quantity": cart_item.quantity,
        "subtotal": float(cart_item.subtotal)
    })

@require_POST
def remove_cart_item_ajax(request):
    cart_id = request.POST.get("cart_id")

    cart_item = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user
    )

    cart_item.delete()

    total_items = Cart.objects.filter(user=request.user).count()
    subtotal = sum(
        item.subtotal for item in Cart.objects.filter(user=request.user)
    )

    return JsonResponse({
        "status": "success",
        "total_items": total_items,
        "subtotal": float(subtotal)
    })

@login_required
@require_POST
def add_to_cart_ajax(request):
    print("ADD TO CART VIEW HIT", request.POST)

    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return JsonResponse({"status": "success"})

@login_required
def checkout(request):
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()

    if request.method == "POST" and request.POST.get("add_address"):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "Address added successfully")
            return redirect("checkout")

    if request.method == "POST" and request.POST.get("buy_now_product_id"):
        request.session["buy_now_product_id"] = request.POST.get("buy_now_product_id")
        return redirect("checkout")

    buy_now_product_id = request.session.get("buy_now_product_id")


    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)

        cart_items = [{
            "product": product,
            "quantity": 1,
            "subtotal": product.offer_price or product.price,
        }]

        total = product.offer_price or product.price

        if request.method == "POST" and request.POST.get("address"):
            request.session["address_id"] = request.POST.get("address")
            return redirect("payment_page")

        return render(request, "checkout.html", {
            "addresses": addresses,
            "cart_items": cart_items,
            "total": total,
            "buy_now": True,
            "form": form,
        })

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("cart")

    total = sum(
        (item.product.offer_price or item.product.price) * item.quantity
        for item in cart_items
    )

    if request.method == "POST" and request.POST.get("address"):
        request.session["address_id"] = request.POST.get("address")
        return redirect("payment_page")

    return render(request, "checkout.html", {
        "addresses": addresses,
        "cart_items": cart_items,
        "total": total,
        "buy_now": False,
        "form": form,
    })


    
@login_required
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    payment_method = request.POST.get("payment_method")
    address_id = request.session.get("address_id")
    buy_now_product_id = request.session.get("buy_now_product_id")

    if not payment_method or not address_id:
        return redirect("checkout")

    address = Address.objects.get(id=address_id)

    if buy_now_product_id:
        product = get_object_or_404(Product, id=buy_now_product_id)
        price = product.offer_price or product.price
        total = price

        order = Order.objects.create(
            user=request.user,
            address=address,
            total=total,
            payment_method=payment_method,
            payment_status="PENDING",
            status="pending",
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=price,
        )
        request.session.pop("buy_now_product_id", None)
        request.session.pop("address_id", None)

    else:
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect("cart")

        total = sum(
            (item.product.offer_price or item.product.price) * item.quantity
            for item in cart_items
        )

        order = Order.objects.create(
            user=request.user,
            address=address,
            total=total,
            payment_method=payment_method,
            payment_status="PENDING",
            status="pending",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.offer_price or item.product.price,
            )

        cart_items.delete()
        request.session.pop("address_id", None)

    if payment_method == "COD":
        return redirect("ordersuccess")

    if payment_method == "STRIPE":
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": f"Order #{order.id}",
                        },
                        "unit_amount": int(total * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(
                f"/payment-success/?order_id={order.id}"
            ),
            cancel_url=request.build_absolute_uri(
                f"/payment-failed/?order_id={order.id}"
            ),
        )

        order.stripe_session_id = session.id
        order.save()

        return redirect(session.url)

    return redirect("checkout")

@never_cache
@staff_member_required(login_url='home')
def update_order_status(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get("status")

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()

    return redirect(request.META.get("HTTP_REFERER", "adminorder"))


    
@login_required
def ordersuccess(request):
    return render(request, "ordersuccess.html")


@login_required
def payment_success(request):
    order_id = request.GET.get("order_id")

    if not order_id:
        return redirect("home")

    order = Order.objects.get(id=order_id, user=request.user)

    order.payment_status = "PAID"
    order.save()

    Cart.objects.filter(user=request.user).delete()
    request.session.pop("address_id", None)

    return redirect("ordersuccess")



def faq(request):
    return render(request,'faq.html')
def privacy(request):
    return render(request,'privacy.html')
def aboutus(request):
    return render(request,'aboutus.html')


@never_cache
def product(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]

    cart_product_ids = []
    wishlist_products = []

    if request.user.is_authenticated:
        cart_product_ids = list(
            Cart.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )

        wishlist_products = list(
            Wishlist.objects.filter(user=request.user)
            .values_list("product_id", flat=True)
        )

    return render(request, "product.html", {
        "product": product,
        "related_products": related_products,
        "cart_product_ids": cart_product_ids,
        "wishlist_products": wishlist_products,
    })


@never_cache
@staff_member_required(login_url='home')
def admindashboard(request):
    total_orders = Order.objects.count()
    total_products = Product.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    revenue = Order.objects.aggregate(total=Sum("total"))["total"] or 0

    context = {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_customers": total_customers,
        "revenue": revenue,
    }

    return render(request, "admindashboard.html", context)

@never_cache
@staff_member_required(login_url='home')
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
@staff_member_required(login_url='home')   
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
@staff_member_required(login_url='home')
def admincustomer(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    customers = User.objects.filter(is_staff=False)

    return render(request, "admincustomer.html", {
        "customers": customers
    })
    

@never_cache
@staff_member_required(login_url='home')
def toggle_customer_block(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")

    user = get_object_or_404(User, id=user_id, is_staff=False)

    user.is_active = not user.is_active
    user.save()

    return redirect("admincustomer")
    
@never_cache
@staff_member_required(login_url='home')
def delete_customer(request, user_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("Access denied")
    user = get_object_or_404(User, id=user_id, is_staff=False)

    if request.method == "POST":
        user.delete()
        return redirect("admincustomer") 
    
@never_cache
@staff_member_required(login_url='home')
def admincategory(request):
    categories = Category.objects.all()

    return render(request, "admincategory.html", {
        "categories": categories
    })
    
@never_cache
@staff_member_required(login_url='home')
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
@staff_member_required(login_url='home')
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
@staff_member_required(login_url='home')
def categorydelete(request, pk):
    if request.method == "POST":
        category = get_object_or_404(Category, pk=pk)

        if category.subcategory_set.exists() or category.product_set.exists():
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
@staff_member_required(login_url='home')
def adminorder(request):
    orders = (
        Order.objects
        .select_related("user")
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    STATUS_CHOICES = [
        "Order Placed",
        "Processing",
        "Shipped",
        "Out for delivery",
        "Delivered",
    ]

    return render(
        request,
        "adminorder.html",
        {
            "orders": orders,
            "status_choices": STATUS_CHOICES,
        },
    )


@never_cache
@staff_member_required(login_url='home')
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = request.POST.get("status")
    order.save()
    return redirect("adminorder")

@never_cache
@staff_member_required(login_url='home')
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
            offer_price=(Decimal(request.POST.get("offer_price"))if request.POST.get("offer_price")else None),
            quantity=int(request.POST.get("quantity")),
            offer=request.POST.get("offer") ,
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
    

def adminlogout(request):
    logout(request)
    return redirect("home")

@never_cache

def userlogout(request):
    logout(request)
    return redirect("login")

@never_cache
@staff_member_required(login_url='home')
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

def search_suggestions(request):
    query = request.GET.get("q", "").strip()

    data = []

    if query:
        products = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=query) |
            Q(subcategory__name__icontains=query)
        )[:5]

        for p in products:
            data.append({
                "id": p.id,
                "name": p.name
            })

    return JsonResponse({"products": data})
    
    
    
    
    
    
    
    
    
    
    
    
    
    