import json

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
# from .forms import WorkoutLogForm
from .models import WorkoutLog

def register_view(request):
    """处理用户注册，确认物理隔离边界"""
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user) #注册后自动签发Session
            return redirect('dashboard')
    else:
        form=UserCreationForm()
    #留出与前端交互的上下文接口
    return render(request, 'auth/register.html', {'form':form})

def login_view(request):
    """处理登录状态机"""
    if request.method=='POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('dashboard')
    else:
        form=AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    """销毁Session,退出登录"""
    logout(request)
    return redirect('login')


def forget_password_view(request):
    """显示忘记密码页面"""
    return render(request, 'auth/forgetPassword.html')

# @login_required(login_url='login') #强制拦截器：未登录直接重定向
# def dashboard_view(request):
#     """私有核心数据展示节点(M1保护)&历史记录提取(M4)"""
#     # 1. 数据提取逻辑：去数据库里捞取数据
#     # 必须用 filter 加上强身份隔离，且按时间倒序排列（最新的在最前面）
#     user_logs=WorkoutLog.objects.filter(user=request.user).order_by('-date')

#     # 2. 封装数据包 (Context)
#     # 这里的 'logs' 是传递给前端的插槽。
#     context={
#         'logs':user_logs
#     }

#     # 3. 抛给前端渲染
#     return render(request, 'core/dashboard.html')

def workout_logger_view(request):
    """处理M3的写入逻辑"""
    if request.method=='POST':
        #1.拦截数据：将前端POST过来的数据塞进过滤器
        form=WorkoutLogForm(request.POST)

        #2.规则校验：如果数据完全符合models.py中定义的类型和边界
        if form.is_valid():
            #3.拦截物理写入：先在内存中生成对象，但不保存到数据库(commit=False)
            log_instance=form.save(commit=False)

            #4.强制身份绑定：将当前发起请求的物理用户，烙印在数据上
            log_instance.user=request.user

            #5.物理写入：安全落库
            log_instance.save()

            #录入成功后，按照常规流转，跳回控制台
            return redirect('dashboard')
    else:
        #如果是GET请求，说明用户刚打开页面，塞一个空的表单给他
        form=WorkoutLogForm()

    #将包含插槽变量的上下文(Context)传给前端模板
    return render(request,'core/workout_logger.html',{'form':form})




from datetime import date, timedelta


def dashboard(request):
    return render(request, "dashboard.html", {
        "active_page": "dashboard"
    })


def program_builder(request):
    today = date.today()

    # 本周周一
    start_of_week = today - timedelta(days=today.weekday())

    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_days.append({
            "weekday": day.strftime("%a"),
            "month_day": day.strftime("%b %d")
        })

    return render(request, "program_builder.html", {
        "active_page": "program_builder",
        "week_days": week_days
    })


def analytics(request):
    return render(request, "analytics.html", {
        "active_page": "analytics",
        "weight_logs": [],
        "personal_records": [],
        "weight_labels_json": json.dumps([]),
        "weight_values_json": json.dumps([]),
        "volume_labels_json": json.dumps([]),
        "volume_values_json": json.dumps([]),
    })