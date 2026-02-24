from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [

    path('api/list/', views.get_exercise_list, name='api_list'),
]