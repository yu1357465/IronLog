from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ExerciseLibrary, WorkoutLog, WorkoutProgram, ProgramExercise


class IronFlowSystemTests(TestCase):

    def setUp(self):
        # Intent: Initialize a sterile test environment with a mock user and baseline exercise data.
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='secure_password_123')
        self.exercise = ExerciseLibrary.objects.create(name='Barbell Squat', category='Legs & Glutes')

        for i in range(7):
            WorkoutProgram.objects.create(user=self.user, day_of_week=i, name='')

    # ==========================================
    # 1. Model Layer Persistence Tests
    # ==========================================
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
            program=program, exercise=self.exercise, order=1, target_weight=100.0, target_sets=5, target_reps=5
        )
        self.assertEqual(program.exercises.count(), 1)
        self.assertEqual(program.exercises.first().target_weight, 100.0)

    # ==========================================
    # 2. View Rendering & Permission Routing
    # ==========================================
    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        # Decision: Verify that unauthenticated requests are safely intercepted and redirected (302).
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_access_for_authenticated_user(self):
        self.client.login(username='test_user', password='secure_password_123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('todays_exercises', response.context)

    # ==========================================
    # 3. Core Logic: POST Interception & Mutations
    # ==========================================
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

    # 【新增测点】测试我们加入的“无头表单”批量保存周计划的功能
    def test_program_builder_post_save_week(self):
        self.client.login(username='test_user', password='secure_password_123')
        p1 = WorkoutProgram.objects.get(user=self.user, day_of_week=0)
        response = self.client.post(reverse('program_builder'), {
            'action': 'save_week',
            'p_id': [p1.id],
            'p_name': ['New Push Day']
        })
        self.assertEqual(response.status_code, 302)
        p1.refresh_from_db()
        self.assertEqual(p1.name, 'New Push Day')

    # 【新增测点】测试我们加入的自定义动作“软删除”机制
    def test_program_builder_soft_delete(self):
        self.client.login(username='test_user', password='secure_password_123')
        custom_ex = ExerciseLibrary.objects.create(name='My Custom Curl', category='Arms', user=self.user)
        response = self.client.post(reverse('program_builder'), {
            'action': 'delete_library_exercise',
            'ex_id': custom_ex.id
        })
        self.assertEqual(response.status_code, 302)
        custom_ex.refresh_from_db()
        self.assertTrue(custom_ex.is_deleted) # 验证物理记录还在，但标记为了已删除

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
        self.assertIn('history_data', response.context) # 验证我们传给图表的新数据流

    # ==========================================
    # 4. Edge Cases & Exception Handling
    # ==========================================
    def test_dashboard_post_invalid_data(self):
        # Intent: Verify that submitting non-numeric strings to float/integer fields triggers safe internal exception handling rather than a 500 Server Error.
        self.client.login(username='test_user', password='secure_password_123')
        data = {
            'exercise_name': ['Barbell Squat'],
            'weight': ['invalid_string'],
            'sets': ['3'],
            'reps': ['8']
        }
        response = self.client.post(reverse('dashboard'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WorkoutLog.objects.filter(user=self.user).count(), 0)

    def test_analytics_muscle_logic_coverage(self):
        # Intent: Ensure the server-side heuristic matching logic successfully parses all required anatomical categories.
        self.client.login(username='test_user', password='secure_password_123')
        categories = ['Chest', 'Back', 'Shoulders', 'Arms', 'Legs', 'Core']
        for cat in categories:
            ex = ExerciseLibrary.objects.create(name=f"Test {cat}", category=cat)
            WorkoutLog.objects.create(user=self.user, exercise=ex, weight=10, sets=1, reps=1)

        response = self.client.get(reverse('analytics'))
        self.assertEqual(response.status_code, 200)

    def test_program_builder_edge_cases(self):
        # Intent: Simulate aggressive user behavior (e.g., deleting a non-existent ID or submitting empty actions) to validate fallback safety.
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