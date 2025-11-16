"""
URL configuration for Health Chatbot API
"""
from django.urls import path
from . import views

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),

    # OpenAPI specification
    path('openapi.yaml', views.openapi_spec, name='openapi_spec'),

    # Chat endpoints
    path('chat/', views.chat, name='chat'),
    path('chat/history/', views.chat_history, name='chat_history'),

    # Meal endpoints
    path('meals/', views.meals_list, name='meals_list'),
    path('meals/<int:meal_id>/', views.meal_detail, name='meal_detail'),

    # Medication endpoints
    path('medications/', views.medications_list, name='medications_list'),
    path('medications/<int:med_id>/', views.medication_detail, name='medication_detail'),

    # Summary endpoints
    path('summary/', views.summary, name='summary'),

    # User profile
    path('profile/', views.user_profile, name='user_profile'),

    # Demo reset
    path('reset/', views.reset_demo, name='reset_demo'),

    # Privacy policy
    path('privacy/', views.privacy_policy, name='privacy_policy'),
]
