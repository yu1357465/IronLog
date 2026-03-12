from django import forms
from .models import WorkoutLog

class WorkoutLogForm(forms.ModelForm):
    """训练日志验证器。它负责将前端传来的杂乱字符串,安全地转化为后端的python对象"""
    class Meta:
        model=WorkoutLog
        #暴露给前端的字段
        fields=['exercise','weight','reps']