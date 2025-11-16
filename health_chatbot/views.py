"""
API Views for Health Chatbot Demo
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

from .models import UserProfile, Meal, Medication, ChatMessage
from .chatbot import HealthChatbot
from .serializers import (
    MealSerializer, MedicationSerializer,
    ChatMessageSerializer, UserProfileSerializer
)


def get_demo_user():
    """Get or create demo user"""
    user, created = UserProfile.objects.get_or_create(
        email='demo@biorhyme.health',
        defaults={
            'name': 'Demo User',
            'age': 30,
            'daily_calorie_goal': 2000,
            'daily_protein_goal': 150,
            'daily_carbs_goal': 250,
            'daily_fat_goal': 65,
            'daily_fiber_goal': 30,
        }
    )
    return user


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'ok',
        'message': 'Biorhyme Health Chatbot Demo is running',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
def openapi_spec(request):
    """
    Serve OpenAPI specification
    """
    import os
    from django.http import FileResponse, Http404
    from django.conf import settings

    spec_path = os.path.join(settings.BASE_DIR, 'openapi.yaml')

    if os.path.exists(spec_path):
        return FileResponse(open(spec_path, 'rb'), content_type='application/x-yaml')
    else:
        raise Http404("OpenAPI spec not found")


@api_view(['POST'])
def chat(request):
    """
    Main chat endpoint
    POST /api/chat/
    {
        "message": "What did I eat today?"
    }
    """
    user_message = request.data.get('message', '').strip()

    if not user_message:
        return Response({
            'error': 'Message is required'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Get demo user
    user = get_demo_user()

    # Process message with chatbot
    chatbot = HealthChatbot(user)
    bot_response = chatbot.process_message(user_message)

    # Save to chat history
    chat_msg = ChatMessage.objects.create(
        user=user,
        user_message=user_message,
        bot_response=bot_response
    )

    return Response({
        'message': user_message,
        'response': bot_response,
        'timestamp': chat_msg.created_at.isoformat()
    })


@api_view(['GET', 'POST'])
def meals_list(request):
    """
    GET /api/meals/ - List all meals
    POST /api/meals/ - Create a new meal
    """
    user = get_demo_user()

    if request.method == 'GET':
        # Query parameters
        days = request.GET.get('days', 7)
        try:
            days = int(days)
        except ValueError:
            days = 7

        date_from = timezone.now().date() - timedelta(days=days)
        meals = Meal.objects.filter(user=user, date__gte=date_from)

        serializer = MealSerializer(meals, many=True)

        # Calculate totals
        totals = meals.aggregate(
            total_calories=Sum('calories'),
            total_protein=Sum('protein'),
            total_carbs=Sum('carbs'),
            total_fat=Sum('fat'),
            total_fiber=Sum('fiber')
        )

        return Response({
            'count': meals.count(),
            'meals': serializer.data,
            'totals': totals
        })

    elif request.method == 'POST':
        # Add user to data
        data = request.data.copy()

        serializer = MealSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({
                'success': True,
                'message': 'Meal logged successfully',
                'meal': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def meal_detail(request, meal_id):
    """
    GET /api/meals/<id>/ - Get meal details
    PUT /api/meals/<id>/ - Update meal
    DELETE /api/meals/<id>/ - Delete meal
    """
    user = get_demo_user()
    meal = get_object_or_404(Meal, id=meal_id, user=user)

    if request.method == 'GET':
        serializer = MealSerializer(meal)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MealSerializer(meal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Meal updated successfully',
                'meal': serializer.data
            })
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        meal_name = meal.meal_name
        meal.delete()
        return Response({
            'success': True,
            'message': f'Deleted {meal_name}'
        })


@api_view(['GET', 'POST'])
def medications_list(request):
    """
    GET /api/medications/ - List all medications
    POST /api/medications/ - Add a new medication
    """
    user = get_demo_user()

    if request.method == 'GET':
        # Filter by active status
        is_active = request.GET.get('active', 'true').lower() == 'true'
        medications = Medication.objects.filter(user=user, is_active=is_active)

        serializer = MedicationSerializer(medications, many=True)
        return Response({
            'count': medications.count(),
            'medications': serializer.data
        })

    elif request.method == 'POST':
        serializer = MedicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({
                'success': True,
                'message': 'Medication added successfully',
                'medication': serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def medication_detail(request, med_id):
    """
    GET /api/medications/<id>/ - Get medication details
    PUT /api/medications/<id>/ - Update medication
    DELETE /api/medications/<id>/ - Delete medication
    """
    user = get_demo_user()
    medication = get_object_or_404(Medication, id=med_id, user=user)

    if request.method == 'GET':
        serializer = MedicationSerializer(medication)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MedicationSerializer(medication, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Medication updated successfully',
                'medication': serializer.data
            })
        return Response({
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        drug_name = medication.drug_name
        medication.delete()
        return Response({
            'success': True,
            'message': f'Deleted {drug_name}'
        })


@api_view(['GET'])
def summary(request):
    """
    GET /api/summary/?period=today|week|month
    Get nutrition summary for a period
    """
    user = get_demo_user()
    period = request.GET.get('period', 'today')

    # Determine date range
    today = timezone.now().date()
    if period == 'today':
        date_from = today
    elif period == 'week':
        date_from = today - timedelta(days=7)
    elif period == 'month':
        date_from = today - timedelta(days=30)
    else:
        date_from = today

    # Get meals
    meals = Meal.objects.filter(user=user, date__gte=date_from)

    # Calculate totals
    totals = meals.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fat=Sum('fat'),
        total_fiber=Sum('fiber')
    )

    # Calculate days
    num_days = (today - date_from).days + 1

    # Daily averages
    averages = {
        'avg_calories': (totals['total_calories'] or 0) / num_days,
        'avg_protein': (totals['total_protein'] or 0) / num_days,
        'avg_carbs': (totals['total_carbs'] or 0) / num_days,
        'avg_fat': (totals['total_fat'] or 0) / num_days,
        'avg_fiber': (totals['total_fiber'] or 0) / num_days,
    }

    # Goals
    goals = {
        'calories': user.daily_calorie_goal,
        'protein': user.daily_protein_goal,
        'carbs': user.daily_carbs_goal,
        'fat': user.daily_fat_goal,
        'fiber': user.daily_fiber_goal,
    }

    # Progress
    progress = {}
    for nutrient in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
        avg_key = f'avg_{nutrient}'
        if goals[nutrient] > 0:
            progress[nutrient] = round((averages[avg_key] / goals[nutrient]) * 100, 1)
        else:
            progress[nutrient] = 0

    return Response({
        'period': period,
        'date_range': {
            'from': date_from.isoformat(),
            'to': today.isoformat(),
            'days': num_days
        },
        'meals_logged': meals.count(),
        'totals': totals,
        'daily_averages': averages,
        'goals': goals,
        'progress_percentage': progress
    })


@api_view(['GET'])
def chat_history(request):
    """
    GET /api/chat/history/?limit=10
    Get chat history
    """
    user = get_demo_user()
    limit = int(request.GET.get('limit', 10))

    messages = ChatMessage.objects.filter(user=user)[:limit]
    serializer = ChatMessageSerializer(messages, many=True)

    return Response({
        'count': messages.count(),
        'messages': serializer.data
    })


@api_view(['GET'])
def user_profile(request):
    """
    GET /api/profile/
    Get user profile
    """
    user = get_demo_user()
    serializer = UserProfileSerializer(user)

    return Response(serializer.data)


@api_view(['POST'])
def reset_demo(request):
    """
    POST /api/reset/
    Reset demo data
    """
    user = get_demo_user()

    # Delete all data
    Meal.objects.filter(user=user).delete()
    Medication.objects.filter(user=user).delete()
    ChatMessage.objects.filter(user=user).delete()

    return Response({
        'success': True,
        'message': 'Demo data has been reset'
    })
