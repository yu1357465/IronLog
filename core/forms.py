from django import forms
from .models import WorkoutLog

class WorkoutLogForm(forms.ModelForm):
    # Decision: Use Django's ModelForm to automatically handle user input validation.
    # Intent: Prevent invalid data from breaking the database by ensuring all user inputs meet the model's strict rules before saving.
    class Meta:
        model = WorkoutLog
        fields = ['exercise', 'weight', 'reps']