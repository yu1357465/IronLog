from django.db import models
from django.conf import settings
from Exercises.models import Exercise

class TrainingSetQuerySet(models.QuerySet):
    def get_rep_prs(self, user):
        from collections import defaultdict
        
        all_sets = self.filter(session__user=user).select_related('exercise', 'session')
        
        exercise_map = defaultdict(list)
        for s in all_sets:
            exercise_map[s.exercise.name].append(s)
            
        rep_records = []
        for name, sets in exercise_map.items():
            sorted_sets = sorted(sets, key=lambda x: (-x.reps, -x.weight))
            
            if not sorted_sets:
                continue
                
            first = sorted_sets[0]
            weight_diff = 0.0
            
            if len(sorted_sets) > 1:
                weight_diff = first.weight - sorted_sets[1].weight
                
            rep_records.append({
                "name": name,
                "reps": first.reps,
                "weight": first.weight,
                "diff": weight_diff,
                "date": first.session.date,
                "category": first.exercise.category
            })

        return sorted(rep_records, key=lambda x: -x['reps'])[:3]

class WorkoutPlan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class PlanEntry(models.Model):
    DAYS = [('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), 
            ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')]
    plan = models.ForeignKey(WorkoutPlan, related_name='entries', on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAYS)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    target_sets = models.IntegerField(default=3)
    target_reps = models.CharField(max_length=20)

class TrainingSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    workout_name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.DateTimeField(auto_now_add=True)

    @property
    def total_sets_count(self):
        return self.sets.count()

class TrainingSet(models.Model):
    session = models.ForeignKey(TrainingSession, related_name='sets', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    weight = models.FloatField()
    reps = models.IntegerField()
    
    objects = TrainingSetQuerySet.as_manager()