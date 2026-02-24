from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import TrainingSet, TrainingSession
from django.db.models import Count

@login_required
def get_analytics_data(request):
    user = request.user
    
    rep_prs = TrainingSet.objects.get_rep_prs(user)
    
    formatted_prs = [{
        "name": pr['name'],
        "reps": pr['reps'],
        "weight": f"{pr['weight']}kg",
        "diff": f"{pr['diff']:+g}kg", 
        "date": pr['date'].strftime('%Y/%m/%d'),
        "category": pr['category']
    } for pr in rep_prs]

    stats = TrainingSet.objects.filter(session__user=user) \
        .values('exercise__category') \
        .annotate(total_sets=Count('id'))

    return JsonResponse({
        "status": "success",
        "muscle_balance": {
            "labels": [s['exercise__category'] for s in stats],
            "values": [s['total_sets'] for s in stats]
        },
        "personal_records": formatted_prs
    })

@login_required
def get_dashboard_summary(request):
    sessions = TrainingSession.objects.filter(user=request.user).order_by('-date')[:5]
    
    recent_activity = [{
        "date": s.date,
        "name": s.workout_name,
        "sets_count": s.total_sets_count
    } for s in sessions]
    
    return JsonResponse({"recent_activity": recent_activity})

@login_required
def manage_plan(request):
    return JsonResponse({"status": "success"})