"""
Serializers for API responses
"""
from rest_framework import serializers
from .models import UserProfile, Meal, Medication, ChatMessage


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'email', 'name', 'age',
            'daily_calorie_goal', 'daily_protein_goal',
            'daily_carbs_goal', 'daily_fat_goal', 'daily_fiber_goal',
            'health_conditions', 'created_at'
        ]


class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = [
            'id', 'meal_name', 'meal_time', 'calories',
            'protein', 'carbs', 'fat', 'fiber',
            'date', 'notes', 'created_at'
        ]


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = [
            'id', 'drug_name', 'dosage', 'frequency',
            'started_date', 'notes', 'is_active',
            'created_at', 'updated_at'
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'user_message', 'bot_response',
            'query_type', 'created_at'
        ]
