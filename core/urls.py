from django.urls import path
from . import views

urlpatterns=[
    #用户访问首页时，直接打入控制台视图
    path('',views.dashboard_view,name='home'),

    #M1权限机制路由
    path('auth/login/',views.login_view,name='login'),
    path('auth/register/',views.register_view,name='register'),
    path('auth/logout',views.logout_view,name='logout'),

    #仪表盘入口(M1保护节点)
    path('dashboard/',views.dashboard_view,name='dashboard'),

    #M3录入节点(Workout Logger)
    path('train/log/',views.workout_logger_view,name='workout_logger'),

    # 新增这一行：专门用来接住前端的 {% url 'program_builder' %}
    path('program-builder/', views.program_builder_view, name='program_builder'),

    # 新增这一行：接住前端的 {% url 'analytics' %}
    path('analytics/', views.analytics_view, name='analytics'),
]