from django.contrib import admin
from .models import ExerciseLibrary, WorkoutLog

# Decision: Register core models to the Django built-in admin panel.
# Intent: This provides an out-of-the-box Content Management System (CMS) to rapidly inspect, troubleshoot, and manipulate database records during the development and testing phases.
admin.site.register(ExerciseLibrary)
admin.site.register(WorkoutLog)