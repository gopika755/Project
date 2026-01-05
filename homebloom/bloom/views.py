from django.shortcuts import render, redirect
from django.contrib.auth import login,get_user_model
from .forms import SignupForm, LoginForm,ForgotPasswordForm, OTPVerifyForm, ResetPasswordForm
from .models import PasswordResetOTP
from django.core.mail import send_mail
from django.contrib import messages
import random
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

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
def signup_view(request):
    form = SignupForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
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
                # ✅ THIS WAS MISSING
                request.session["reset_user_id"] = user.id
                return redirect("reset_password")

    return render(request, "verify_otp.html", {"form": form})


def reset_password(request):
    user_id = request.session.get("reset_user_id")

    if not user_id:
        return redirect("forgot")  # ❌ NOT reset_password

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


def profile(request):
    return render(request,'profile.html')
def order(request):
    return render(request,'order.html')
def detail(reqeust):
    return render(reqeust,'detail.html')
def adminorder(request):
    return render(request,'adminorder.html')
def addaddress(request):
    return render(request,'addaddress.html')
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
            login(request, user)
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
    return render(request,'adminproduct.html')
def productedit(request):
    return render(request,'productedit.html')
def admincustomer(request):
    return render(request,'admincustomer.html')
def admincategory(request):
    return render(request,'admincategory.html')
def categoryedit(request):
    return render (request,'categoryedit.html')
def admincoupon(request):
    return render(request,'admincoupon.html')
def couponedit(request):
    return render(request,'couponedit.html')
def chairs(request):
    return render(request,'chairs.html')
def addproduct(request):
    return render(request,'addproduct.html')
    
# Create your views here.
