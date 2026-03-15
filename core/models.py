from django.db import models
from django.contrib.auth.models import User

# Database: Predefined actions
class ExerciseLibrary(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# Historical Workout Logs
class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)
    weight = models.FloatField()

    sets = models.IntegerField(default=1)
    reps = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.date}"

# Program Builder: Planning Logic
class WorkoutProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    day_of_week = models.IntegerField(default=0)     # Day index: 0=Mon, 6=Sun
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def day_name(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.day_of_week]

    def __str__(self):
        return f"{self.user.username} - Day {self.day_of_week}: {self.name}"

# Workout Plan Checklist
class ProgramExercise(models.Model):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)
    target_sets = models.IntegerField(default=3)
    target_reps = models.IntegerField(default=10)
    target_weight = models.FloatField(null=True, blank=True)
    order = models.IntegerField(default=0) # Sequence of actions

    class Meta:
        ordering = ['order'] #  Automatically sort data in order

    def __str__(self):
        return f"{self.program.name} : {self.exercise.name}"