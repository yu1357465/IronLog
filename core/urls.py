from django.urls import path
from django.contrib.auth import views as auth_views
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

    # ==========================================
    # Django 内置重置密码系统 (Built-in Password Reset System)
    # ==========================================

    # 1. 触发报错的缺口：提交邮箱的页面 (映射到你的 forgetPassword.html)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/auth/forgetPassword.html'), name='password_reset'),

    # 2. 邮件发送成功后的提示页面 (Django 要求必须有这个名字的路由)
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/auth/password_reset_done.html'), name='password_reset_done'),

    # 3. 用户点击邮件里的加密链接后，跳转到的修改密码页面
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/auth/password_reset_confirm.html'), name='password_reset_confirm'),

    # 4. 密码修改成功后的最终提示页面
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/auth/password_reset_complete.html'), name='password_reset_complete'),
]