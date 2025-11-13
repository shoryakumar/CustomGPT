"""
URL configuration for Custom GPT Demo
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home_view(request):
    return JsonResponse({
        'message': 'Welcome to Biorhyme Health Custom GPT Demo',
        'endpoints': {
            'chat': '/api/chat/',
            'meals': '/api/meals/',
            'medications': '/api/medications/',
            'summary': '/api/summary/',
            'health': '/api/health/',
        },
        'documentation': 'See README.md for usage instructions'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/', include('health_chatbot.urls')),
]
