from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from django.db.models import Q
import json
from datetime import datetime, timedelta
from .forms import WorkoutLogForm
from .models import WorkoutLog, ExerciseLibrary, WorkoutProgram, ProgramExercise

def register_view(request):
    """Handles user registration and establishes session boundaries."""
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save()
            # Intent: Automatically authenticate and issue a session token immediately after successful registration to reduce user friction.
            login(request, user)
            return redirect('dashboard')
    else:
        form=UserCreationForm()

    # Decision: Expose the validation form context to the frontend for error rendering.
    return render(request, 'core/auth/register.html', {'form':form})

def login_view(request):
    """Manages the authentication state machine."""
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
    """Destroys the user session and handles secure logout."""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    """M1 Dashboard Core: Renders the targeted workout program for the current or queried day."""

    # Decision: Fallback to the current system day if no specific day parameter is provided via the URL.
    current_day_name = datetime.now().strftime('%A')
    selected_day = request.GET.get('day', current_day_name)

    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if selected_day not in valid_days:
        selected_day = current_day_name

    # Mechanism: Map human-readable day strings to integer indexes (0-6) to align with the database schema for faster querying.
    day_index = valid_days.index(selected_day)

    # Fetch the specific workout program associated with the resolved day index.
    todays_program = WorkoutProgram.objects.filter(user=request.user, day_of_week=day_index).first()

    if todays_program:
        todays_exercises = todays_program.exercises.all().select_related('exercise').order_by('order')

        # Mechanism: Dynamically aggregate Personal Record (PR) weights for each scheduled exercise by querying the historical log.
        for p_ex in todays_exercises:
            pr_record = WorkoutLog.objects.filter(
                user=request.user,
                exercise=p_ex.exercise,
                weight__gt=0
            ).order_by('-weight').first()

            # Decision: Attach the PR data in-memory to the queryset instances to avoid secondary frontend API calls.
            p_ex.pr_weight = pr_record.weight if pr_record else None
    else:
        todays_exercises = []

    # Handle form submissions for logging completed workouts or deleting erroneous entries.
    if request.method == 'POST':
        if 'delete_log_id' in request.POST:
            log_id = request.POST.get('delete_log_id')
            try:
                WorkoutLog.objects.get(id=log_id, user=request.user).delete()
            except WorkoutLog.DoesNotExist:
                pass
            # Refresh the view while maintaining the active day context.
            return redirect(f"/dashboard/?day={selected_day}")

        ex_names = request.POST.getlist('exercise_name')
        weights = request.POST.getlist('weight')
        sets_list = request.POST.getlist('sets')
        reps_list = request.POST.getlist('reps')

        # Mechanism: Retrieve the list of explicitly checked exercises from the frontend payload.
        checked_exercises = request.POST.getlist('done_exercise_names')

        # Decision: Fallback mechanism. If no exercises are explicitly checked,
        # assume the user intends to log the entire routine as completed.
        if not checked_exercises:
            checked_exercises = ex_names

        for i in range(len(ex_names)):
            name_val = ex_names[i]

            # Strict backend validation: Skip any payload row that was not explicitly marked as done.
            if name_val not in checked_exercises:
                continue

            w_val = weights[i].strip() if i < len(weights) else ''
            s_val = sets_list[i].strip() if i < len(sets_list) else ''
            r_val = reps_list[i].strip() if i < len(reps_list) else ''

            if w_val and s_val and r_val:
                try:
                    # Mechanism (Multi-tenant Isolation): Query the exercise library ensuring cross-user data boundaries. Fallback to public exercises if a private one doesn't exist.
                    exercise_obj = ExerciseLibrary.objects.filter(
                        name__iexact=name_val,
                        is_deleted=False
                    ).filter(Q(user__isnull=True) | Q(user=request.user)).first()

                    # Decision: Auto-generate a private exercise entry if the user logs an unlisted exercise.
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

        # Redirect to preserve the selected day state in the URL parameters.
        return redirect(f"/dashboard/?day={selected_day}")

    # Retrieve historical logs for the current week.
    today_date = timezone.now().date()
    start_of_week = today_date - timedelta(days=today_date.weekday())
    user_logs = WorkoutLog.objects.filter(user=request.user, date__gte=start_of_week).order_by('-date')

    # Calculate circular pagination for weekly day navigation.
    days_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_index = days_list.index(selected_day)
    prev_day = days_list[(current_index - 1) % 7]
    next_day = days_list[(current_index + 1) % 7]

    # Resolve dynamic titles for the frontend UI based on the active program state.
    if todays_program and todays_program.name:
        program_title = todays_program.name
    else:
        program_title = "Rest Day"

    if selected_day == current_day_name:
        day_label = f"Today ({selected_day})"
    else:
        day_label = selected_day

    context = {
        # Inject context flag to trigger active state highlighting in the sidebar navigation.
        'active_page': 'dashboard',
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
    """Handles explicit workout log insertions (M3)."""
    if request.method=='POST':
        # Mechanism: Leverage Django ModelForm for strict schema validation against the POST payload.
        form=WorkoutLogForm(request.POST)

        if form.is_valid():
            # Decision: Suspend database commit (commit=False) to allow programmatic injection of the user ID.
            log_instance=form.save(commit=False)

            # Enforce strict user-data binding to prevent unauthorized data spoofing.
            log_instance.user=request.user

            log_instance.save()

            return redirect('dashboard')
    else:
        form=WorkoutLogForm()

    return render(request,'core/workout_logger.html',{'form':form})

@login_required(login_url='login')
def program_builder_view(request):
    """M2 Program Builder: Orchestrates the weekly Kanban board and exercise library."""

    # Action Router: Handle various POST mutations (add, delete, soft-delete, re-order, reset).
    if request.method == 'POST':
        action = request.POST.get('action')

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
                    ex_name = new_ex_name.strip()

                    # Mechanism: Prevent duplicate exercise creations by querying existing public/private entries before instantiation.
                    exercise = ExerciseLibrary.objects.filter(
                        name__iexact=ex_name,
                        is_deleted=False
                    ).filter(Q(user__isnull=True) | Q(user=request.user)).first()

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

                parsed_weight = float(weight_val) if weight_val and weight_val.strip() else None

                ProgramExercise.objects.create(
                    program=program,
                    exercise=exercise,
                    target_weight=parsed_weight,
                    target_sets=int(sets),
                    target_reps=int(reps),
                    order=current_count + 1
                )
            except Exception as e:
                print(f"Error adding exercise: {e}")
            return redirect('program_builder')

        elif action == 'delete_exercise':
            p_ex_id = request.POST.get('p_ex_id')
            try:
                # Decision: Enforce user-level permission checks during deletion to prevent IDOR (Insecure Direct Object Reference) vulnerabilities.
                ProgramExercise.objects.filter(id=p_ex_id, program__user=request.user).delete()
            except Exception as e:
                print(f"Error deleting scheduled exercise: {e}")
            return redirect('program_builder')

        elif action == 'delete_library_exercise':
            ex_id = request.POST.get('ex_id')
            try:
                # Mechanism (Soft Delete): Mark custom exercises as deleted rather than executing a hard SQL DELETE, preserving historical log integrity.
                ex = ExerciseLibrary.objects.get(id=ex_id, user=request.user)
                ex.is_deleted = True
                ex.save()
            except Exception as e:
                print(f"Error soft-deleting library exercise: {e}")
            return redirect('program_builder')

        elif action == 'save_week':
            p_ids = request.POST.getlist('p_id')
            p_names = request.POST.getlist('p_name')

            # Batch update week titles using parallel array iteration (zip).
            for pid, pname in zip(p_ids, p_names):
                WorkoutProgram.objects.filter(id=pid, user=request.user).update(name=pname.strip())
            return redirect('program_builder')

        elif action == 'reset_week':
            # Destructive Action: Cascade delete all exercises within the user's weekly programs.
            programs = WorkoutProgram.objects.filter(user=request.user)
            for p in programs:
                p.name = ''
                p.save()
                p.exercises.all().delete()
            return redirect('program_builder')

    # Retrieve both global public exercises and user-specific private exercises.
    library_exercises = ExerciseLibrary.objects.filter(
        Q(user__isnull=True) | Q(user=request.user),
        is_deleted=False
    ).order_by('category', 'name')

    user_programs = WorkoutProgram.objects.filter(user=request.user).order_by('day_of_week')

    # Counter-Intuitive Mechanism (Silent Initialization): Automatically seed 7 empty program instances for first-time users to ensure the Kanban board grid renders correctly without requiring manual setup.
    if user_programs.count() < 7:
        WorkoutProgram.objects.filter(user=request.user).delete()
        for i in range(7):
            WorkoutProgram.objects.create(
                user=request.user,
                name='',
                day_of_week=i
            )
        user_programs = WorkoutProgram.objects.filter(user=request.user).order_by('day_of_week')

    context = {
        'active_page': 'program_builder',
        'library_exercises': library_exercises,
        'weekly_programs': user_programs
    }
    return render(request, 'core/program_builder.html', context)

@login_required(login_url='login')
def analytics_view(request):
    """M4 Analytics Core: Aggregates PRs, trend history, and categorical muscle balance."""

    # Mechanism: Pre-sort the queryset by weight (descending) and date to prepare for efficient PR extraction.
    raw_logs = WorkoutLog.objects.filter(
        user=request.user,
        weight__gt=0
    ).select_related('exercise').order_by('-weight', '-date')

    seen_exercises = set()
    top_logs = []

    # Decision (In-memory Deduplication): Use a hash set (O(1) lookup) to filter out sub-maximal lifts for each exercise, extracting only the true PR.
    for log in raw_logs:
        ex_name = log.exercise.name

        if ex_name not in seen_exercises:
            top_logs.append(log)
            seen_exercises.add(ex_name)

            # Performance Optimization: Halt the iteration early once the top 6 unique PRs are identified to conserve CPU cycles.
        if len(top_logs) == 6:
            break

    balance_values = [0, 0, 0, 0, 0, 0]

    all_logs = WorkoutLog.objects.filter(user=request.user).select_related('exercise')

    # Mechanism (Heuristic Matching): Scan exercise names and categories against keyword dictionaries to approximate training volume distribution for the radar chart.
    for log in all_logs:
        ex_name = (log.exercise.name or '').upper()
        ex_cat = (log.exercise.category or '').upper()
        search_str = f"{ex_name} {ex_cat}"

        if any(kw in search_str for kw in ['CHEST', 'BENCH', 'PEC', 'PUSH']):
            balance_values[0] += 1
        elif any(kw in search_str for kw in ['BACK', 'PULL', 'ROW', 'LAT']):
            balance_values[1] += 1
        elif any(kw in search_str for kw in ['SHOULDER', 'RAISE', 'PRESS', 'DELT']):
            balance_values[2] += 1
        elif any(kw in search_str for kw in ['ARM', 'CURL', 'TRI', 'BI', 'EXTENSION']):
            balance_values[3] += 1
        elif any(kw in search_str for kw in ['LEG', 'SQUAT', 'GLUTE', 'PRESS', 'DEADLIFT']):
            balance_values[4] += 1
        elif any(kw in search_str for kw in ['CORE', 'ABS', 'CRUNCH', 'PLANK']):
            balance_values[5] += 1
        else:
            pass

    # Ensure chronological ordering for accurate trend line plotting.
    valid_logs = WorkoutLog.objects.filter(user=request.user, weight__gt=0).order_by('date')

    # Data Structuring: Group dates and weights by exercise name to supply the frontend Chart.js datasets.
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

    available_exercises = list(history_data.keys())

    # Decision: Serialize the Python dictionaries and lists into JSON payloads for direct hydration into the frontend JavaScript context.
    available_exercises_json = json.dumps(available_exercises)


    context = {
        'active_page': 'analytics',
        'logs': top_logs,
        'muscle_balance_values': json.dumps(balance_values),
        'history_data': json.dumps(history_data),
        'available_exercises_json': available_exercises_json,
        'available_exercises': available_exercises,
    }

    return render(request, 'core/analytics.html', context)