from django.urls import path
from . import views

urlpatterns=[
    #M1权限机制路由
    path('auth/login/',views.login_view,name='login'),
    path('auth/register/',views.register_view,name='register'),
    path('auth/logout',views.logout_view,name='logout'),

    #仪表盘入口(M1保护节点)
    path('dashboard/',views.dashboard_view,name='dashboard'),
]