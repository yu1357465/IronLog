from django.urls import path
from . import views

urlpatterns=[
    path('',views.dashboard_view,name='home'),
    path('auth/login/',views.login_view,name='login'),
    path('auth/register/',views.register_view,name='register'),
    path('auth/logout',views.logout_view,name='logout'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('train/log/',views.workout_logger_view,name='workout_logger'),
    path('program-builder/', views.program_builder_view, name='program_builder'),
    path('analytics/', views.analytics_view, name='analytics'),
]