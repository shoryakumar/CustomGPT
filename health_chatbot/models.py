"""
Simplified models for Custom GPT Demo
No authentication - single demo user
"""
from django.db import models
from django.utils import timezone


def get_current_date():
    """Return current date (not datetime)"""
    return timezone.now().date()


class UserProfile(models.Model):
    """Demo user profile"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, default="Demo User")
    age = models.IntegerField(null=True, blank=True)

    # Health goals
    daily_calorie_goal = models.FloatField(default=2000)
    daily_protein_goal = models.FloatField(default=150)
    daily_carbs_goal = models.FloatField(default=250)
    daily_fat_goal = models.FloatField(default=65)
    daily_fiber_goal = models.FloatField(default=30)

    health_conditions = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.name} ({self.email})"


class Meal(models.Model):
    """Meal entries"""
    MEAL_TIMES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='meals')
    meal_name = models.CharField(max_length=200)
    meal_time = models.CharField(max_length=20, choices=MEAL_TIMES, default='breakfast')

    # Nutrition
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    fiber = models.FloatField(default=0)

    # Metadata
    date = models.DateField(default=get_current_date)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'meals'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.meal_name} - {self.date}"


class Medication(models.Model):
    """Medication tracking"""
    FREQUENCIES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('three_times_daily', 'Three Times Daily'),
        ('as_needed', 'As Needed'),
    ]

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='medications')
    drug_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50, choices=FREQUENCIES)

    started_date = models.DateField(default=get_current_date)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medications'
        ordering = ['-is_active', 'drug_name']

    def __str__(self):
        return f"{self.drug_name} {self.dosage}"


class ChatMessage(models.Model):
    """Chat history"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chat_messages')
    user_message = models.TextField()
    bot_response = models.TextField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    query_type = models.CharField(max_length=50, blank=True)  # e.g., 'nutrition_query', 'meal_log', etc.

    class Meta:
        db_table = 'chat_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat at {self.created_at}"
