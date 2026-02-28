from django.urls import path
from . import views

urlpatterns=[
    #用户访问首页时，直接打入控制台视图
    path('',views.dashboard,name='home'),

    #M1权限机制路由
    path('auth/login/',views.login_view,name='login'),
    path('auth/register/',views.register_view,name='register'),
    path('auth/password-reset/', views.forget_password_view, name='forget_password'),
    path('auth/logout',views.logout_view,name='logout'),

    #仪表盘入口(M1保护节点)
    path('dashboard/',views.dashboard,name='dashboard'),

    #M3录入节点(Workout Logger)
    path('train/log/',views.workout_logger_view,name='workout_logger'),


    path("program_builder/", views.program_builder, name="program_builder"),

    path("analytics/", views.analytics, name="analytics"),
]