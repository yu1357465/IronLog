from django.db import models
from django.contrib.auth.models import User

class ExerciseLibrary(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class WorkoutLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)
    weight = models.FloatField()

    # === 原代码注释掉 ===
    # reps = models.IntegerField()
    # date = models.DateTimeField(auto_now_add=True)

    # === 改动后的代码 ===
    sets = models.IntegerField(default=1)  # 新增：记录组数 (Sets)，完美对接前端的新UI
    reps = models.IntegerField()           # 记录次数 (Reps)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.name} - {self.date}"

# ==========================================
# 以下为新增代码：支撑 Program Builder 的核心模具
# ==========================================

class WorkoutProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True) # 允许为空，空就是休息日

    # 【核心新增】：时间坐标锚点，0=周一，6=周日
    day_of_week = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # 【极其优雅的属性拦截器】：直接在后端把数字转换成星期几的名字发给前端
    @property
    def day_name(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.day_of_week]

    def __str__(self):
        return f"{self.user.username} - Day {self.day_of_week}: {self.name}"

class ProgramExercise(models.Model):
    """
    计划动作清单表 (连接 计划 和 动作库)
    规定了某个计划里具体包含哪些动作，以及目标组数和次数。
    """
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(ExerciseLibrary, on_delete=models.PROTECT)

    # 这是你在制定计划时设定的“目标值”，供前端加载时作为默认占位符(Placeholder)使用
    target_sets = models.IntegerField(default=3)
    target_reps = models.IntegerField(default=10)
    # 【核心新增】：允许重量为空（留空代表自适应），保留一位小数
    target_weight = models.FloatField(null=True, blank=True)
    order = models.IntegerField(default=0) # 动作的先后顺序 (例如：深蹲排第1，腿屈伸排第2)

    class Meta:
        ordering = ['order'] # 提取数据时自动按顺序排列

    def __str__(self):
        return f"{self.program.name} : {self.exercise.name}"