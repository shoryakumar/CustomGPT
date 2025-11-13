"""
Django Admin configuration
"""
from django.contrib import admin
from .models import UserProfile, Meal, Medication, ChatMessage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'age', 'created_at']
    search_fields = ['email', 'name']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['meal_name', 'meal_time', 'calories', 'date', 'user']
    list_filter = ['meal_time', 'date']
    search_fields = ['meal_name', 'user__email']
    date_hierarchy = 'date'


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['drug_name', 'dosage', 'frequency', 'is_active', 'user']
    list_filter = ['frequency', 'is_active']
    search_fields = ['drug_name', 'user__email']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_message_short', 'query_type', 'created_at']
    list_filter = ['query_type', 'created_at']
    search_fields = ['user_message', 'bot_response', 'user__email']
    date_hierarchy = 'created_at'

    def user_message_short(self, obj):
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_short.short_description = 'User Message'
