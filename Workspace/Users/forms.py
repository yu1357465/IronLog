from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm

User = get_user_model()

# --- Register ---
class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

# --- Login ---
class UserLoginForm(AuthenticationForm):

    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'your.email@example.com'
    }), label="Email Address")
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your password'
    }))

# --- Forgot Password ---
class UserPasswordResetForm(PasswordResetForm):
   
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your registered email'
    }))