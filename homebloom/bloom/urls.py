from django.urls import path
from bloom import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',views.home,name='home'),
    path('furniture',views.furniture,name='furniture'),
    path('walldecor',views.walldecor,name='walldecor'),
    path('kitchen',views.kitchen,name='kitchen'),
    path('lighting',views.lighting,name='lighting'),
    path('bath',views.bath,name='bath'),
    path('login/',views.login_view,name='login'),
    path('signup',views.signup_view,name='signup'),
    path('forgot',views.forgot,name='forgot'),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("password-changed/", views.password_changed, name="password_changed"),
    path('profile',views.profile,name='profile'),
    path('order',views.order,name='order'),
    path('detail',views.detail,name='detail'),
    path('adminorder',views.adminorder,name='adminorder'),
    path('addaddress',views.addaddress,name='addaddress'),
    path('wishlist',views.wishlist,name='wishlist'),
    path('cart',views.cart,name='cart'),
    path('checkout',views.checkout,name='checkout'),
    path('faq',views.faq,name='faq'),
    path('parivacy',views.privacy,name='privacy'),
    path('aboutus',views.aboutus,name='aboutus'),
    path('product/',views.product,name='product'),
    path('adminpanel/',views.adminpanel,name='adminpanel'),
    path('admindashboard/',views.admindashboard,name='admindashboard'),
    path('adminproduct/',views.adminproduct,name='adminproduct'),
    path("productedit/<int:pk>/", views.productedit, name="productedit"),
    path('product/toggle/<int:id>/', views.product_toggle_status, name='product_toggle'),
    path('admincutomer/',views.admincustomer,name='admincustomer'),
    path("dashboard/customers/delete/<int:user_id>/", views.delete_customer, name="delete_customer"),   
    path('admincategory',views.admincategory,name='admincategory'),
    path("categoryedit/<int:pk>/", views.categoryedit, name="categoryedit"),
    path("categoryadd/", views.categoryadd, name="categoryadd"),
    path('admincoupon/',views.admincoupon,name='admincoupon'),
    path('couponedit/',views.couponedit,name='couponedit'),
    path('chairs',views.chairs,name='chairs'),
    path("add_product/", views.add_product, name="addproduct"),
    path("categorydelete/<int:pk>/", views.categorydelete, name="categorydelete"),
    path("logout/", views.userlogout, name="userlogout"),
    path("adminlogout/", views.adminlogout, name="adminlogout"),
    path("adminbanner/", views.banner_add, name="banner_add"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),




]