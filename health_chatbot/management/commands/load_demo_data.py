"""
Management command to load demo data
Usage: python manage.py load_demo_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from health_chatbot.models import UserProfile, Meal, Medication


class Command(BaseCommand):
    help = 'Load demo data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Loading demo data...')

        # Create demo user
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
                'health_conditions': ['Type 2 Diabetes', 'Hypertension']
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created demo user'))
        else:
            self.stdout.write('  Demo user already exists')

        # Clear existing data
        Meal.objects.filter(user=user).delete()
        Medication.objects.filter(user=user).delete()

        # Create meals for the past week
        today = timezone.now().date()

        meals_data = [
            # Today
            {
                'day_offset': 0,
                'meal_name': 'Oatmeal with Berries',
                'meal_time': 'breakfast',
                'calories': 350,
                'protein': 12,
                'carbs': 58,
                'fat': 8,
                'fiber': 8
            },
            {
                'day_offset': 0,
                'meal_name': 'Grilled Chicken Salad',
                'meal_time': 'lunch',
                'calories': 420,
                'protein': 38,
                'carbs': 25,
                'fat': 18,
                'fiber': 6
            },
            {
                'day_offset': 0,
                'meal_name': 'Greek Yogurt',
                'meal_time': 'snack',
                'calories': 150,
                'protein': 15,
                'carbs': 18,
                'fat': 3,
                'fiber': 1
            },
            # Yesterday
            {
                'day_offset': 1,
                'meal_name': 'Scrambled Eggs with Toast',
                'meal_time': 'breakfast',
                'calories': 380,
                'protein': 22,
                'carbs': 32,
                'fat': 16,
                'fiber': 4
            },
            {
                'day_offset': 1,
                'meal_name': 'Salmon with Brown Rice',
                'meal_time': 'lunch',
                'calories': 520,
                'protein': 42,
                'carbs': 45,
                'fat': 18,
                'fiber': 5
            },
            {
                'day_offset': 1,
                'meal_name': 'Stir-Fry Vegetables with Tofu',
                'meal_time': 'dinner',
                'calories': 380,
                'protein': 24,
                'carbs': 38,
                'fat': 14,
                'fiber': 8
            },
            # 2 days ago
            {
                'day_offset': 2,
                'meal_name': 'Protein Smoothie',
                'meal_time': 'breakfast',
                'calories': 320,
                'protein': 28,
                'carbs': 42,
                'fat': 6,
                'fiber': 5
            },
            {
                'day_offset': 2,
                'meal_name': 'Turkey Sandwich',
                'meal_time': 'lunch',
                'calories': 450,
                'protein': 32,
                'carbs': 48,
                'fat': 12,
                'fiber': 6
            },
            {
                'day_offset': 2,
                'meal_name': 'Beef Stir-Fry',
                'meal_time': 'dinner',
                'calories': 480,
                'protein': 38,
                'carbs': 32,
                'fat': 20,
                'fiber': 4
            },
            # 3 days ago
            {
                'day_offset': 3,
                'meal_name': 'Avocado Toast',
                'meal_time': 'breakfast',
                'calories': 340,
                'protein': 10,
                'carbs': 36,
                'fat': 18,
                'fiber': 12
            },
            {
                'day_offset': 3,
                'meal_name': 'Chicken Burrito Bowl',
                'meal_time': 'lunch',
                'calories': 580,
                'protein': 42,
                'carbs': 62,
                'fat': 16,
                'fiber': 10
            },
            # 4 days ago
            {
                'day_offset': 4,
                'meal_name': 'Pancakes with Fruit',
                'meal_time': 'breakfast',
                'calories': 420,
                'protein': 12,
                'carbs': 68,
                'fat': 10,
                'fiber': 4
            },
            {
                'day_offset': 4,
                'meal_name': 'Tuna Salad',
                'meal_time': 'lunch',
                'calories': 380,
                'protein': 35,
                'carbs': 22,
                'fat': 16,
                'fiber': 5
            },
            {
                'day_offset': 4,
                'meal_name': 'Pasta with Marinara',
                'meal_time': 'dinner',
                'calories': 520,
                'protein': 18,
                'carbs': 82,
                'fat': 12,
                'fiber': 6
            },
        ]

        meals_created = 0
        for meal_data in meals_data:
            day_offset = meal_data.pop('day_offset')
            meal_date = today - timedelta(days=day_offset)

            Meal.objects.create(
                user=user,
                date=meal_date,
                **meal_data
            )
            meals_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Created {meals_created} meals'))

        # Create medications
        medications_data = [
            {
                'drug_name': 'Metformin',
                'dosage': '500mg',
                'frequency': 'twice_daily',
                'notes': 'Take with meals'
            },
            {
                'drug_name': 'Lisinopril',
                'dosage': '10mg',
                'frequency': 'once_daily',
                'notes': 'For blood pressure'
            },
            {
                'drug_name': 'Vitamin D',
                'dosage': '2000 IU',
                'frequency': 'once_daily',
                'notes': 'Supplement'
            },
        ]

        meds_created = 0
        for med_data in medications_data:
            Medication.objects.create(
                user=user,
                started_date=today - timedelta(days=30),
                **med_data
            )
            meds_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Created {meds_created} medications'))

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Demo data loaded successfully!'))
        self.stdout.write('')
        self.stdout.write(f'User: {user.email}')
        self.stdout.write(f'Meals: {meals_created}')
        self.stdout.write(f'Medications: {meds_created}')
        self.stdout.write('')
        self.stdout.write('You can now test the chatbot!')
        self.stdout.write('Try: "What did I eat today?"')
