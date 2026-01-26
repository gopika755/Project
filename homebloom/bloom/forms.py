from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm,PasswordResetForm,UserCreationForm
from django import forms
from .models import Product ,SubCategory,Address
from django.contrib.auth import get_user_model


User = get_user_model()

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
        })
    )
class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your email"
        })
    )    
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField()

class OTPVerifyForm(forms.Form):
    otp = forms.CharField(max_length=6)

class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "New Password"}),
        label="New Password",
        min_length=6
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}),
        label="Confirm Password",
        min_length=6
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")

        if not self.user:
            raise forms.ValidationError("User not found or session expired.")

        return cleaned_data

    def save(self):
      
        self.user.set_password(self.cleaned_data["password1"])
        self.user.save()
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'offer_price', 'quantity', 
            'offer', 'description', 'image1', 'image2', 'image3', 'image4'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product name'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price'}),
            'offer_price': forms.NumberInput(attrs={'placeholder': 'Offer price'}),
            'quantity': forms.NumberInput(attrs={'placeholder': 'Stock quantity'}),
            'offer': forms.NumberInput(attrs={'placeholder': 'Discount %'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description', 'rows': 3}),
        }
class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcategory name'}),
        }
        
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ["user"]
