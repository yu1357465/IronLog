from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

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
    return render(request, 'core/register.html', {'form':form})

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
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """销毁Session,退出登录"""
    logout(request)
    return redirect('login')

@login_required(login_url='login') #强制拦截器：未登录直接重定向
def dashboard_view(request):
    """私有核心数据展示节点(M1保护)"""
    return render(request, 'core/dashboard.html')