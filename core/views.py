from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone  # 从 Django 工具箱拿时区工具
from django.db.models import Count
from django.db.models import Q
import json
from datetime import datetime, timedelta
from .forms import WorkoutLogForm
from .models import WorkoutLog, ExerciseLibrary, WorkoutProgram, ProgramExercise

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
    return render(request, 'core/auth/register.html', {'form':form})

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
    return render(request, 'core/auth/login.html', {'form': form})

def logout_view(request):
    """销毁Session,退出登录"""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    """M1 核心驾驶舱：展示今日或指定日期的训练计划"""

    # 1. 智能日期嗅探器：优先读取 URL 里的 ?day= 参数，如果没有，就取现实中的今天
    current_day_name = datetime.now().strftime('%A')
    selected_day = request.GET.get('day', current_day_name)

    # === 改动后的代码 ===
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if selected_day not in valid_days:
        selected_day = current_day_name

    # 【核心翻译】：将字符串 'Monday' 翻译为数字 0, 'Tuesday' 为 1... 匹配底层数据库
    day_index = valid_days.index(selected_day)

    # 【核心修复】：向数据库查询时，使用真正的字段名 day_of_week，并传入数字
    todays_program = WorkoutProgram.objects.filter(user=request.user, day_of_week=day_index).first()

    if todays_program:
        todays_exercises = todays_program.exercises.all().select_related('exercise').order_by('order')
    else:
        todays_exercises = []

    # === 2. 写入拦截 (POST) ===
    if request.method == 'POST':
        if 'delete_log_id' in request.POST:
            log_id = request.POST.get('delete_log_id')
            try:
                WorkoutLog.objects.get(id=log_id, user=request.user).delete()
            except WorkoutLog.DoesNotExist:
                pass
            return redirect(f"/dashboard/?day={selected_day}") # 删完原地刷新

        ex_names = request.POST.getlist('exercise_name')
        weights = request.POST.getlist('weight')
        sets_list = request.POST.getlist('sets')
        reps_list = request.POST.getlist('reps')

        for i in range(len(ex_names)):
            name_val = ex_names[i]
            w_val = weights[i].strip() if i < len(weights) else ''
            s_val = sets_list[i].strip() if i < len(sets_list) else ''
            r_val = reps_list[i].strip() if i < len(reps_list) else ''

            if w_val and s_val and r_val:
                try:
                    # 🚨 核心防重与多租户隔离机制同步：先查后建
                    exercise_obj = ExerciseLibrary.objects.filter(
                        name__iexact=name_val,
                        is_deleted=False
                    ).filter(Q(user__isnull=True) | Q(user=request.user)).first()

                    # 🚨 如果库里完全没有这个动作，才为你新建一个专属的
                    if not exercise_obj:
                        exercise_obj = ExerciseLibrary.objects.create(
                            name=name_val,
                            category='Auto-Generated',
                            user=request.user
                        )

                    WorkoutLog.objects.create(
                        user=request.user, exercise=exercise_obj,
                        weight=float(w_val), sets=int(s_val), reps=int(r_val)
                    )
                except ValueError:
                    pass
        # 保存完毕，携带当前天数参数原地重定向
        return redirect(f"/dashboard/?day={selected_day}")

    # === 3. 提取历史数据 (GET) ===
    today_date = timezone.now().date()
    start_of_week = today_date - timedelta(days=today_date.weekday())
    user_logs = WorkoutLog.objects.filter(user=request.user, date__gte=start_of_week).order_by('-date')

    # === 4. 计算前后翻页的星期字符串 ===
    days_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_index = days_list.index(selected_day)
    prev_day = days_list[(current_index - 1) % 7]
    next_day = days_list[(current_index + 1) % 7]

    # 【核心修复】：重新生成前端需要的标题和星期标签
    if todays_program and todays_program.name:
        program_title = todays_program.name
    else:
        program_title = "Rest Day"

    # 如果选中的刚好是现实中的今天，加个 "Today" 前缀显得更智能
    if selected_day == current_day_name:
        day_label = f"Today ({selected_day})"
    else:
        day_label = selected_day

    # 【核心修复】：把这两个变量塞回给前端
    context = {
        'active_page': 'dashboard',             # 🚨 [核心魔法]：发射 Dashboard 高亮信号
        'selected_day': selected_day,
        'todays_program': todays_program,
        'todays_exercises': todays_exercises,
        'logs': user_logs,
        'prev_day': prev_day,
        'next_day': next_day,
        'todays_workout_title': program_title,  # <- 补回标题
        'day_label': day_label,                 # <- 补回星期标签
    }
    return render(request, 'core/dashboard.html', context)

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

@login_required(login_url='login')
def program_builder_view(request):
    """M2 计划构建核心：支撑七天看板视图与预加载"""

    # ==========================================
    # 【核心新增】：拦截动作添加与删除的 POST 请求
    # ==========================================
    if request.method == 'POST':
        action = request.POST.get('action')

        # 1. 拦截：添加新动作
        if action == 'add_exercise':
            p_id = request.POST.get('program_id')
            ex_id = request.POST.get('exercise_id')
            new_ex_name = request.POST.get('new_exercise_name')
            # 【新增】：捕获强制分类和重量
            new_ex_cat = request.POST.get('new_exercise_category', 'Custom')
            weight_val = request.POST.get('weight')

            sets = request.POST.get('sets', 3)
            reps = request.POST.get('reps', 10)

            try:
                program = WorkoutProgram.objects.get(id=p_id, user=request.user)
                if new_ex_name and new_ex_name.strip():
                    ex_name = new_ex_name.strip()

                    # 🚨 核心防重机制：先去整个大库里找（无论是系统的还是你自己的），只要有同名且没被删的，就直接拿来用
                    exercise = ExerciseLibrary.objects.filter(
                        name__iexact=ex_name, # 忽略大小写匹配
                        is_deleted=False
                    ).filter(Q(user__isnull=True) | Q(user=request.user)).first()

                    # 如果掘地三尺都找不到，才真正为你新建一个专属动作
                    if not exercise:
                        exercise = ExerciseLibrary.objects.create(
                            name=ex_name,
                            category=new_ex_cat,
                            user=request.user
                        )
                elif ex_id:
                    exercise = ExerciseLibrary.objects.get(id=ex_id)
                else:
                    raise ValueError("Must provide an exercise.")

                current_count = program.exercises.count()

                # 安全转换重量值
                parsed_weight = float(weight_val) if weight_val and weight_val.strip() else None

                ProgramExercise.objects.create(
                    program=program,
                    exercise=exercise,
                    target_weight=parsed_weight, # 【新增写入】
                    target_sets=int(sets),
                    target_reps=int(reps),
                    order=current_count + 1
                )
            except Exception as e:
                print(f"❌ 添加动作失败: {e}")
            return redirect('program_builder')

        # 🚨 核心抢救：补回彻底丢失的删除右侧看板动作的逻辑
        elif action == 'delete_exercise':
            p_ex_id = request.POST.get('p_ex_id')
            try:
                # 安全校验：确保只能删自己当前计划里的动作
                ProgramExercise.objects.filter(id=p_ex_id, program__user=request.user).delete()
            except Exception as e:
                print(f"❌ 删除排期动作失败: {e}")
            return redirect('program_builder')

        # 5. 拦截：软删除自定义动作 (Soft Delete)
        elif action == 'delete_library_exercise':
            ex_id = request.POST.get('ex_id')
            try:
                # 严密的安全校验：只能删自己创建的动作！
                ex = ExerciseLibrary.objects.get(id=ex_id, user=request.user)
                ex.is_deleted = True  # 盖上隐形斗篷，不真删，保全历史日志
                ex.save()
            except Exception as e:
                print(f"❌ 软删除动作失败或越权访问: {e}")
            return redirect('program_builder')

        # 3. 拦截：保存整周计划名称
        elif action == 'save_week':
            p_ids = request.POST.getlist('p_id')
            p_names = request.POST.getlist('p_name')

            # 使用 zip 函数并行遍历两个数组
            for pid, pname in zip(p_ids, p_names):
                # 批量更新每个盒子的名字
                WorkoutProgram.objects.filter(id=pid, user=request.user).update(name=pname.strip())
            return redirect('program_builder')

        # 4. 拦截：一键重置整周数据 (破坏性操作)
        elif action == 'reset_week':
            programs = WorkoutProgram.objects.filter(user=request.user)
            for p in programs:
                p.name = '' # 清空标题
                p.save()
                p.exercises.all().delete() # 物理清空里面的所有动作
            return redirect('program_builder')

    # 1. 抓取全局动作库，发送给左侧面板,我们要查两种动作：1. user 为空 (系统公共动作) 或者 2. user 是当前登录用户的 (私有动作)
    library_exercises = ExerciseLibrary.objects.filter(
        Q(user__isnull=True) | Q(user=request.user),
        is_deleted=False
    ).order_by('category', 'name')

    # 2. 抓取该用户的 7 天排期计划，按周一到周日的顺序排列
    user_programs = WorkoutProgram.objects.filter(user=request.user).order_by('day_of_week')

    # 3. 【核心机制：静默初始化】
    # 如果用户的库里连7天的数据都没有（新用户第一次来），系统就在后台瞬间帮他建好7个空相框
    if user_programs.count() < 7:
        # 为了防呆，先清空可能残留的残缺数据
        WorkoutProgram.objects.filter(user=request.user).delete()
        for i in range(7):
            WorkoutProgram.objects.create(
                user=request.user,
                name='',  # 初始名字为空，等用户在前端看板上敲字
                day_of_week=i
            )
        # 重新抓取刚刚建好的7个相框
        user_programs = WorkoutProgram.objects.filter(user=request.user).order_by('day_of_week')

    # 将数据装包发给前线
    context = {
        'active_page': 'program_builder',       # 🚨 [核心魔法]：发射 Program Builder 高亮信号
        'library_exercises': library_exercises,
        'weekly_programs': user_programs
    }
    return render(request, 'core/program_builder.html', context)

@login_required(login_url='login')
def analytics_view(request):
    """M4 数据大屏核心：计算雷达图与个人最高记录 (PR)"""

    # 1. 计算 Personal Records (PR)
    # 绕过 SQLite 的限制，直接按重量降序，获取历史前 6 个最重的合法记录
    top_logs = WorkoutLog.objects.filter(
        user=request.user,
        weight__gt=0  # 重量必须大于0
    ).select_related('exercise').order_by('-weight')[:6]

    # 2. 计算 Muscle Balance 雷达图数据
    # 对应前端的顺序: ["Chest", "Back", "Shoulders", "Arms", "Legs & Glutes", "Core"]
    balance_values = [0, 0, 0, 0, 0, 0]

    # 将用户的所有的训练记录调出，并附带动作信息
    all_logs = WorkoutLog.objects.filter(user=request.user).select_related('exercise')

    # 智能嗅探引擎：同时匹配分类名和动作名
    for log in all_logs:
        ex_name = (log.exercise.name or '').upper()
        ex_cat = (log.exercise.category or '').upper()
        search_str = f"{ex_name} {ex_cat}"

        # Chest
        if any(kw in search_str for kw in ['CHEST', 'BENCH', 'PEC', 'PUSH']):
            balance_values[0] += 1
        # Back
        elif any(kw in search_str for kw in ['BACK', 'PULL', 'ROW', 'LAT']):
            balance_values[1] += 1
        # Shoulders
        elif any(kw in search_str for kw in ['SHOULDER', 'RAISE', 'PRESS', 'DELT']):
            balance_values[2] += 1
        # Arms
        elif any(kw in search_str for kw in ['ARM', 'CURL', 'TRI', 'BI', 'EXTENSION']):
            balance_values[3] += 1
        # Legs & Glutes
        elif any(kw in search_str for kw in ['LEG', 'SQUAT', 'GLUTE', 'PRESS', 'DEADLIFT']):
            balance_values[4] += 1
        # Core
        elif any(kw in search_str for kw in ['CORE', 'ABS', 'CRUNCH', 'PLANK']):
            balance_values[5] += 1
        else:
            # 如果什么都没匹配上，为了雷达图好看，均匀散布或默认加到某一项
            pass

    # ==========================================
    # 【新增逻辑】：计算折线图趋势数据 (Trend Data)
    # ==========================================
    # 1. 提取所有有实际重量的记录，并按日期升序排列 (时间轴必须是从早到晚)
    valid_logs = WorkoutLog.objects.filter(user=request.user, weight__gt=0).order_by('date')

    # 2. 构建一个字典，格式如： {'Bench Press': {'dates': ['Mar 01', 'Mar 05'], 'weights': [50, 55]}}
    history_data = {}
    for log in valid_logs:
        ex_name = log.exercise.name
        if not ex_name:
            continue

        if ex_name not in history_data:
            history_data[ex_name] = {'dates': [], 'weights': []}

        # 提取短日期格式 (例如 'Mar 12') 和重量
        formatted_date = log.date.strftime('%b %d')
        history_data[ex_name]['dates'].append(formatted_date)
        history_data[ex_name]['weights'].append(log.weight)

    # 3. 提取所有有记录的动作名字，供前端生成下拉菜单
    available_exercises = list(history_data.keys())

    # === 改动后的 context：加入新数据 ===
    context = {
        'active_page': 'analytics',             # 🚨 [核心魔法]：发射 Analytics 高亮信号
        'logs': top_logs,
        'muscle_balance_values': json.dumps(balance_values),
        # 【新增】：传给前端的折线图数据包
        'history_data': json.dumps(history_data),
        'available_exercises': available_exercises,
    }

    return render(request, 'core/analytics.html', context)