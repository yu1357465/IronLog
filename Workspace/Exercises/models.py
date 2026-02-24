from django.db import models

class Exercise(models.Model):

    CATEGORY_CHOICES = [
        ('Chest', 'Chest'),
        ('Back', 'Back'),
        ('Shoulders', 'Shoulders'),
        ('Arms', 'Arms'),
        ('Legs', 'Legs'), 
        ('Core', 'Core'),
    ]

 
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    search_vector = models.TextField(blank=True, null=True) 

    class Meta:
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"