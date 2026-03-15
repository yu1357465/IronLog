
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ExerciseLibrary, WorkoutLog, WorkoutProgram, ProgramExercise


class IronFlowSystemTests(TestCase):

    #System core link test
    def setUp(self):
        #Test environment initialization: Simulating users and basic data
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='secure_password_123')
        self.exercise = ExerciseLibrary.objects.create(name='Barbell Squat', category='Legs & Glutes')

        for i in range(7):
            WorkoutProgram.objects.create(user=self.user, day_of_week=i, name='')

    #  Model layer testing
    def test_workout_log_creation(self):
        log = WorkoutLog.objects.create(
            user=self.user, exercise=self.exercise, weight=100.5, sets=4, reps=8
        )
        self.assertEqual(log.weight, 100.5)
        self.assertEqual(log.user.username, 'test_user')

    def test_program_creation(self):
        program = WorkoutProgram.objects.filter(user=self.user, day_of_week=0).first()
        program.name = 'Heavy Leg Day'
        program.save()
        ProgramExercise.objects.create(
            program=program, exercise=self.exercise, order=1, target_sets=5, target_reps=5
        )
        self.assertEqual(program.exercises.count(), 1)

    # View rendering and permission testing
    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access_for_authenticated_user(self):
        self.client.login(username='test_user', password='secure_password_123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('todays_exercises', response.context)

    # Core logic POST interception test
    def test_program_builder_post_add_exercise(self):
        self.client.login(username='test_user', password='secure_password_123')
        program = WorkoutProgram.objects.get(user=self.user, day_of_week=0)
        response = self.client.post(reverse('program_builder'), {
            'action': 'add_exercise',
            'program_id': program.id,
            'new_exercise_name': 'Incline Bench Press',
            'new_exercise_category': 'Chest',
            'weight': '60',
            'sets': '3',
            'reps': '10'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ExerciseLibrary.objects.filter(name='Incline Bench Press').exists())

    def test_program_builder_post_reset_week(self):
        self.client.login(username='test_user', password='secure_password_123')
        response = self.client.post(reverse('program_builder'), {'action': 'reset_week'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProgramExercise.objects.count(), 0)

    def test_dashboard_post_save_workout(self):
        self.client.login(username='test_user', password='secure_password_123')
        data = {
            'exercise_name': ['Barbell Squat'],
            'weight': ['100'],
            'sets': ['3'],
            'reps': ['8']
        }
        response = self.client.post(reverse('dashboard'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 1)

    def test_dashboard_delete_log(self):
        self.client.login(username='test_user', password='secure_password_123')
        log = WorkoutLog.objects.create(user=self.user, exercise=self.exercise, weight=50, sets=3, reps=10)
        response = self.client.post(reverse('dashboard'), {'delete_log_id': log.id})
        self.assertFalse(WorkoutLog.objects.filter(id=log.id).exists())

    def test_analytics_view_rendering(self):
        self.client.login(username='test_user', password='secure_password_123')
        response = self.client.get(reverse('analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('muscle_balance_values', response.context)



    def test_dashboard_post_invalid_data(self):
        #Test dashboard: Submitting illegal data should be skipped by the system
        self.client.login(username='test_user', password='secure_password_123')
        data = {
            'exercise_name': ['Barbell Squat'],
            'weight': ['abc'],  # 非法重量，触发 views.py 中的 ValueError 捕获
            'sets': ['3'],
            'reps': ['8']
        }
        response = self.client.post(reverse('dashboard'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 0)

    def test_analytics_muscle_logic_coverage(self):
        #Test Analysis Page: Matching logic covering all muscle group categories
        self.client.login(username='test_user', password='secure_password_123')

        categories = ['Chest', 'Back', 'Shoulders', 'Arms', 'Legs', 'Core']
        for cat in categories:
            ex = ExerciseLibrary.objects.create(name=f"Test {cat}", category=cat)
            WorkoutLog.objects.create(user=self.user, exercise=ex, weight=10, sets=1, reps=1)

        response = self.client.get(reverse('analytics'))
        self.assertEqual(response.status_code, 200)


    def test_program_builder_edge_cases(self):
        #Test plan builder: Simulates deletion of branches that do not exist or involve illegal actions.
        self.client.login(username='test_user', password='secure_password_123')

        response = self.client.post(reverse('program_builder'), {
            'action': 'delete_exercise',
            'p_ex_id': 9999
        })
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse('program_builder'), {
            'action': 'add_exercise',
            'program_id': WorkoutProgram.objects.filter(user=self.user).first().id,
            'new_exercise_name': '',
        }, follow=False)

        self.assertEqual(response.status_code, 302)

        target_url = reverse('program_builder')
        self.assertTrue(response.url.endswith(target_url) or response.url == target_url)