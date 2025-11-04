# ==============================================
# authentication/views.py (UPDATED)
# ==============================================

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegistrationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # All users (including superadmin) need admin approval
            user.is_active = False
            user.approval_status = 'pending'
            user.save()
            
            messages.success(
                request, 
                'Registration request submitted successfully! Your account is pending admin approval. '
                'You will receive notification once your account is approved.'
            )
            
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if user is superadmin - they can login without approval
            if user.role == 'superadmin':
                # Auto-approve superadmin if not already approved
                if not user.is_active or user.approval_status != 'approved':
                    user.approval_status = 'approved'
                    user.is_active = True
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            
            # For other users, check approval status
            if user.approval_status == 'pending':
                messages.warning(
                    request, 
                    'Your account is pending admin approval. Please wait for approval before logging in.'
                )
            elif user.approval_status == 'rejected':
                messages.error(
                    request, 
                    'Your account registration was rejected. Please contact administrator for more information.'
                )
            elif user.approval_status == 'approved' and user.is_active:
                # Approved users can login - no re-approval needed for existing users
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is not active. Please contact administrator.')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'authentication/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')