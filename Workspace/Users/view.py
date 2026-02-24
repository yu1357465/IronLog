# users/views.py

from django.shortcuts import render, redirect  
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm  
from django.shortcuts import render, redirect
from django.urls import path 
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model

def register_view(request):
   
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('user:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'user/register.html', {'form': form})

def login_view(request):

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user:index')
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = UserLoginForm()
    return render(request, 'user/login.html', {'form': form})


# --- Forgot Password ---


User = get_user_model()


def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
       
        if not User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email not found.'}, status=404)
        

        otp = str(random.randint(100000, 999999))
        
        request.session['reset_otp'] = otp
        request.session['reset_email'] = email
        request.session.set_expiry(300) 
        
        print(f"DEBUG OTP: {otp}")
        
        return JsonResponse({'status': 'success', 'message': 'Verification code sent.'})
    
    return render(request, 'user/forget_password.html')


def check_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        
        if session_otp and user_otp == session_otp:
            
            request.session['otp_verified'] = True
            return JsonResponse({'status': 'success'})
        
        return JsonResponse({'status': 'error', 'message': 'Invalid or expired code.'}, status=400)


def update_password(request):
    
    if not request.session.get('otp_verified'):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized request.'}, status=403)

    if request.method == 'POST':
        new_password = request.POST.get('password')
        email = request.session.get('reset_email')
        
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        request.session.flush()
        
        return JsonResponse({'status': 'success', 'message': 'Password updated.'})