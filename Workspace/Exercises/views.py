from django.http import JsonResponse
from .models import Exercise
from django.db.models import Q

def get_exercise_list(request):
  
    category = request.GET.get('category', 'All')
    search_query = request.GET.get('search', '').strip()


    exercises = Exercise.objects.all()


    if category != 'All':
        exercises = exercises.filter(category=category)


    if search_query:
        exercises = exercises.filter(
            Q(name__icontains=search_query) | 
            Q(category__icontains=search_query)
        )


    data = [
        {
            "id": ex.pk,
            "name": ex.name,
            "category": ex.category,
        } for ex in exercises
    ]

    return JsonResponse({"status": "success", "data": data})