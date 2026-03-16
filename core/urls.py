from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Decision: Route the root URL directly to the dashboard rather than a static landing page.
    # Intent: Immediately engage authenticated users with their core data upon login.
    path('', views.dashboard_view, name='home'),

    # Authentication State Management
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout', views.logout_view, name='logout'),

    # Core Application Modules
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('train/log/', views.workout_logger_view, name='workout_logger'),
    path('program-builder/', views.program_builder_view, name='program_builder'),
    path('analytics/', views.analytics_view, name='analytics'),

    # ==========================================
    # Built-in Password Reset Workflow
    # ==========================================
    # Decision: Leverage Django's native authentication views for password recovery instead of custom implementations.
    # Intent: Ensure cryptographic security (token generation/validation) and prevent common vulnerabilities like timing attacks.

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/auth/forgetPassword.html'), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/auth/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/auth/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/auth/password_reset_complete.html'), name='password_reset_complete'),
]