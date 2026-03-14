import json
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from core.models import ExerciseLibrary

class Command(BaseCommand):
    help = 'Read Exercise_library.json and seed the database with default exercises'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'Exercise_Library', 'Exercise_library.json')

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'❌ File not found: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        success_count = 0
        self.stdout.write(self.style.WARNING('🚀 Initializing default exercise library from JSON...'))

        for item in raw_data:
            # Data is clean, insert directly into the database
            obj, created = ExerciseLibrary.objects.get_or_create(
                name=item["Name"],
                defaults={'category': item["Category"]}
            )

            if created:
                success_count += 1

        self.stdout.write(self.style.SUCCESS(f'✅ Database seeding complete! Successfully imported {success_count} standard exercises.'))