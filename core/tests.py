from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import ExerciseLibrary, WorkoutLog, WorkoutProgram, ProgramExercise

class IronFlowSystemTests(TestCase):
    """系统核心链路测试类"""

    def setUp(self):
        """
        测试环境初始化（每次执行测试前会自动运行）
        模拟一个真实用户和一些基础动作数据
        """
        # 1. 启动虚拟浏览器客户端
        self.client = Client()

        # 2. 创造一个测试用户
        self.user = User.objects.create_user(username='test_user', password='secure_password_123')

        # 3. 在动作库里预埋一个标准动作
        self.exercise = ExerciseLibrary.objects.create(name='Barbell Squat', category='Legs & Glutes')

    # ==========================================
    # 模块一：数据库模型层测试 (Model Tests)
    # ==========================================
    def test_workout_log_creation(self):
        """测试核心业务：用户能否成功生成一条训练记录"""
        log = WorkoutLog.objects.create(
            user=self.user,
            exercise=self.exercise,
            weight=100.5,
            sets=4,
            reps=8
        )
        # 断言：检查存入数据库的数据是否精确无误
        self.assertEqual(log.weight, 100.5)
        self.assertEqual(log.sets, 4)
        self.assertEqual(log.user.username, 'test_user')
        self.assertEqual(log.exercise.name, 'Barbell Squat')

    def test_program_creation(self):
        """测试排期引擎：能否为用户创建一个星期一的训练计划"""
        program = WorkoutProgram.objects.create(
            user=self.user,
            day_of_week=0, # 0 代表星期一
            name='Heavy Leg Day'
        )
        # 将动作关联到这一天的计划中
        ProgramExercise.objects.create(
            program=program,
            exercise=self.exercise,
            order=1,
            target_sets=5,
            target_reps=5
        )
        # 断言：计划名字是否正确，且该计划下是否有 1 个动作
        self.assertEqual(program.name, 'Heavy Leg Day')
        self.assertEqual(program.exercises.count(), 1)

    # ==========================================
    # 模块二：视图与路由层测试 (View & Route Tests)
    # ==========================================
    def test_login_page_renders_successfully(self):
        """测试入口：未登录用户访问登录页，应当返回 200 成功状态码"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        # 确保加载了正确的 HTML 模板
        self.assertTemplateUsed(response, 'core/auth/login.html')

    def test_dashboard_requires_login(self):
        """测试权限隔离：未登录用户强闯 Dashboard，必须被拦截并踢回登录页"""
        response = self.client.get(reverse('dashboard'))
        # 302 代表重定向 (Redirect)
        self.assertEqual(response.status_code, 302)

        # 【核心修复】：剥离硬编码！使用 reverse 动态获取系统真实的登录路由前缀
        expected_login_url = reverse('login')
        self.assertTrue(response.url.startswith(expected_login_url))

    def test_dashboard_access_for_authenticated_user(self):
        """测试授权通行：已登录用户访问 Dashboard，应当顺利放行并渲染数据"""
        # 模拟真实用户的登录动作
        self.client.login(username='test_user', password='secure_password_123')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # 检查上下文中是否包含了预期的变量
        self.assertIn('todays_exercises', response.context)
        self.assertIn('logs', response.context)