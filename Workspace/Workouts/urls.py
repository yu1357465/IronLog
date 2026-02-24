from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    
    path('api/dashboard/', views.get_dashboard_summary, name='dashboard_api'),
    
    path('api/plan/', views.manage_plan, name='plan_api'),
    
    path('api/analytics/', views.get_analytics_data, name='analytics_api'),
]