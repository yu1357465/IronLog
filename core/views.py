from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone  # 从 Django 工具箱拿时区工具
from django.db.models import Count
import json
from datetime import datetime, timedelta
from .forms import WorkoutLogForm
from .models import WorkoutLog, ExerciseLibrary, WorkoutProgram, ProgramExercise

# Auth: User Registration
def register_view(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form=UserCreationForm()
    return render(request, 'core/auth/register.html', {'form':form})

# Auth: Handle user login
def login_view(request):
    if request.method=='POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            user=form.get_user()
            login(request,user)
            return redirect('dashboard')
    else:
        form=AuthenticationForm()
    return render(request, 'core/auth/login.html', {'form': form})

# Auth: Handle user logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard: Main control panel

@login_required(login_url='login')
def dashboard_view(request):
    """ M1 Core Cockpit: Displays training plans for today or a specified date """

    # View workouts by time
    current_day_name = datetime.now().strftime('%A')
    selected_day = request.GET.get('day', current_day_name)

    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if selected_day not in valid_days:
        selected_day = current_day_name
    day_index = valid_days.index(selected_day)

    todays_program = WorkoutProgram.objects.filter(user=request.user, day_of_week=day_index).first()
    if todays_program:
        todays_exercises = todays_program.exercises.all().select_related('exercise').order_by('order')
    else:
        todays_exercises = []

    # Process the commands sent to the server when the user want to save or delete
    if request.method == 'POST':
        # Delete record
        if 'delete_log_id' in request.POST:
            log_id = request.POST.get('delete_log_id')
            try:
                WorkoutLog.objects.get(id=log_id, user=request.user).delete()
            except WorkoutLog.DoesNotExist:
                pass
            return redirect(f"/dashboard/?day={selected_day}")

       # Batch Create Record
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
                    exercise_obj, _ = ExerciseLibrary.objects.get_or_create(
                        name=name_val, defaults={'category': 'Auto-Generated'}
                    )
                    WorkoutLog.objects.create(
                        user=request.user, exercise=exercise_obj,
                        weight=float(w_val), sets=int(s_val), reps=int(r_val)
                    )
                except ValueError:
                    pass
        return redirect(f"/dashboard/?day={selected_day}")

    # extract history record (fixed time period)
    today_date = timezone.now().date()
    start_of_week = today_date - timedelta(days=today_date.weekday())
    user_logs = WorkoutLog.objects.filter(user=request.user, date__gte=start_of_week).order_by('-date')

    # Calculate the day of the week strings for the previous and next pages
    days_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_index = days_list.index(selected_day)
    prev_day = days_list[(current_index - 1) % 7]
    next_day = days_list[(current_index + 1) % 7]

    if todays_program and todays_program.name:
        program_title = todays_program.name
    else:
        program_title = "Rest Day"

    # Prettier
    if selected_day == current_day_name:
        day_label = f"Today ({selected_day})"
    else:
        day_label = selected_day

    context = {
        'selected_day': selected_day,
        'todays_program': todays_program,
        'todays_exercises': todays_exercises,
        'logs': user_logs,
        'prev_day': prev_day,
        'next_day': next_day,
        'todays_workout_title': program_title,
        'day_label': day_label,
    }
    return render(request, 'core/dashboard.html', context)

def workout_logger_view(request):
    """Handling the write logic for M3"""
    if request.method=='POST':
        # Verify compliance with requirements
        form=WorkoutLogForm(request.POST)

        if form.is_valid():
            log_instance=form.save(commit=False)
            log_instance.user=request.user
            log_instance.save()
            return redirect('dashboard')
    else:
        #If it's a GET request, it means the user has just opened the page. So give them an empty form.
        form=WorkoutLogForm()

    return render(request,'core/workout_logger.html',{'form':form})

# log first

@login_required(login_url='login')
def program_builder_view(request):
    """M2 Project Core Development: Supporting the 7-Day Kanban View and Preloading"""

    if request.method == 'POST':
        action = request.POST.get('action')

        # Add new action
        if action == 'add_exercise':
            p_id = request.POST.get('program_id')
            ex_id = request.POST.get('exercise_id')
            new_ex_name = request.POST.get('new_exercise_name')
            new_ex_cat = request.POST.get('new_exercise_category', 'Custom')
            weight_val = request.POST.get('weight')

            sets = request.POST.get('sets', 3)
            reps = request.POST.get('reps', 10)

            try:
                program = WorkoutProgram.objects.get(id=p_id, user=request.user)
                if new_ex_name and new_ex_name.strip():
                    exercise, _ = ExerciseLibrary.objects.get_or_create(
                        name=new_ex_name.strip(),
                        defaults={'category': new_ex_cat}
                    )
                elif ex_id:
                    exercise = ExerciseLibrary.objects.get(id=ex_id)
                else:
                    raise ValueError("Must provide an exercise.")

                current_count = program.exercises.count()
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
                print(f"❌ Failed to add action: {e}")
            return redirect('program_builder')

        # Delete action
        elif action == 'delete_exercise':
            p_ex_id = request.POST.get('p_ex_id')
            try:
                ProgramExercise.objects.filter(id=p_ex_id, program__user=request.user).delete()
            except Exception as e:
                print(f"❌ The deletion failed: {e}")
            return redirect('program_builder')

        # Save the name of the weekly plan
        elif action == 'save_week':
            p_ids = request.POST.getlist('p_id')
            p_names = request.POST.getlist('p_name')

            for pid, pname in zip(p_ids, p_names):
                WorkoutProgram.objects.filter(id=pid, user=request.user).update(name=pname.strip())
            return redirect('program_builder')

        # Reset the entire week's data
        elif action == 'reset_week':
            programs = WorkoutProgram.objects.filter(user=request.user)
            for p in programs:
                p.name = ''
                p.save()
                p.exercises.all().delete()
            return redirect('program_builder')

    library_exercises = ExerciseLibrary.objects.filter(is_deleted=False).order_by('category', 'name')

    user_programs = WorkoutProgram.objects.filter(user=request.user).order_by('day_of_week')

    # If a user's database does not even contain 7 days' worth of data , the system will create an empty for them.
    if user_programs.count() < 7:
        # Clear all
        WorkoutProgram.objects.filter(user=request.user).delete()
        for i in range(7):
            WorkoutProgram.objects.create(
                user=request.user,
                name='',
                day_of_week=i
            )

        user_programs = WorkoutProgram.objects.filter(user=request.user).order_by('day_of_week')

    context = {
        'library_exercises': library_exercises,
        'weekly_programs': user_programs
    }
    return render(request, 'core/program_builder.html', context)

@login_required(login_url='login')
def analytics_view(request):
    """M4 Dashboard Core: Calculating Radar Charts and Personal Bests (PR)"""

    top_logs = WorkoutLog.objects.filter(
        user=request.user,
        weight__gt=0
    ).select_related('exercise').order_by('-weight')[:6]

    # Radar chart
    balance_values = [0, 0, 0, 0, 0, 0]

    # Retrieve user's training records
    all_logs = WorkoutLog.objects.filter(user=request.user).select_related('exercise')

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
            pass


    # record sort by date
    valid_logs = WorkoutLog.objects.filter(user=request.user, weight__gt=0).order_by('date')

    # Build a dictionary
    history_data = {}
    for log in valid_logs:
        ex_name = log.exercise.name
        if not ex_name:
            continue

        if ex_name not in history_data:
            history_data[ex_name] = {'dates': [], 'weights': []}

        formatted_date = log.date.strftime('%b %d')
        history_data[ex_name]['dates'].append(formatted_date)
        history_data[ex_name]['weights'].append(log.weight)

    # For front-end generation of dropdown menus
    available_exercises = list(history_data.keys())

    context = {
        'logs': top_logs,
        'muscle_balance_values': json.dumps(balance_values),
        'history_data': json.dumps(history_data),
        'available_exercises': available_exercises,
    }

    return render(request, 'core/analytics.html', context)