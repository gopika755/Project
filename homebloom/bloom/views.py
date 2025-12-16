from django.shortcuts import render


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
def login(request):
    return render(request,'login.html')
def signup(reqeust):
    return render(reqeust,'signup.html')
def forgot(request):
    return render(request,'forgot.html')
def profile(request):
    return render(request,'profile.html')
def order(request):
    return render(request,'order.html')
def detail(reqeust):
    return render(reqeust,'detail.html')


# Create your views here.
