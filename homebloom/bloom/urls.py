from django.urls import path
from bloom import views

urlpatterns = [
    path('',views.home,name='home'),
    path('furniture',views.furniture,name='furniture'),
    path('walldecor',views.walldecor,name='walldecor'),
    path('kitchen',views.kitchen,name='kitchen'),
    path('lighting',views.lighting,name='lighting'),
    path('bath',views.bath,name='bath'),
    path('login',views.login,name='login'),
    path('signup',views.signup,name='signup'),
    path('forgot',views.forgot,name='forgot'),
    path('profile',views.profile,name='profile'),
    path('order',views.order,name='order'),
    path('detail',views.detail,name='detail')
]