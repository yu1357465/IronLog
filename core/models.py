from django.db import models
from django.contrib.auth.models import User

class ExerciseLibrary(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Decision: Use PROTECT instead of CASCADE for the exercise link.
    # Intent: Prevent accidental deletion of past workout history if an exercise is removed from the library.
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)
    weight = models.FloatField()

    # Intent: Added 'sets' to accurately reflect real-world gym tracking, where users do multiple sets of the same exercise.
    sets = models.IntegerField(default=1)
    reps = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.date}"

class WorkoutProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)

    # Decision: Store days as integers (0=Monday, 6=Sunday) instead of text strings.
    # Intent: Numbers are faster for the database to sort and search.
    day_of_week = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Decision: Use a property decorator to translate the day number into a readable name.
    # Intent: Keep the database lightweight with numbers, while making it easy for the front-end pages to display text.
    @property
    def day_name(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.day_of_week]

    def __str__(self):
        return f"{self.user.username} - Day {self.day_of_week}: {self.name}"

class ProgramExercise(models.Model):
    # Decision: Use related_name='exercises' to easily fetch all exercises belonging to a specific program.
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)

    # Intent: Set default values to act as helpful placeholders when a user builds a new routine.
    target_sets = models.IntegerField(default=3)
    target_reps = models.IntegerField(default=10)

    # Intent: Allow target_weight to be empty, letting users adapt their weight on the day rather than forcing a strict plan.
    target_weight = models.FloatField(null=True, blank=True)

    # Intent: Keep track of the order so exercises don't get mixed up.
    order = models.IntegerField(default=0)

    class Meta:
        # Intent: Always return exercises in the order the user arranged them, not by when they were added to the database.
        ordering = ['order']

    def __str__(self):
        return f"{self.program.name} : {self.exercise.name}"