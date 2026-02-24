from django.db import models
from django.contrib.auth.models import User

class ExerciseLibrary(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)
    weight = models.FloatField()
    reps = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.date}"