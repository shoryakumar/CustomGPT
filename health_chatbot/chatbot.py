"""
Simple chatbot logic for demo
Analyzes user questions and queries database
"""
import re
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from .models import Meal, Medication, UserProfile


class HealthChatbot:
    """Simple rule-based chatbot for demo purposes"""

    def __init__(self, user_profile):
        self.user = user_profile

    def process_message(self, message):
        """
        Process user message and return response
        """
        message_lower = message.lower()

        # Determine intent
        if self._is_meal_query(message_lower):
            return self._handle_meal_query(message_lower)
        elif self._is_nutrition_query(message_lower):
            return self._handle_nutrition_query(message_lower)
        elif self._is_medication_query(message_lower):
            return self._handle_medication_query(message_lower)
        elif self._is_goal_query(message_lower):
            return self._handle_goal_query(message_lower)
        elif self._is_log_meal_intent(message_lower):
            return self._handle_log_meal_intent(message)
        elif self._is_add_medication_intent(message_lower):
            return self._handle_add_medication_intent(message)
        else:
            return self._handle_general_query(message_lower)

    # Intent detection methods
    def _is_meal_query(self, message):
        keywords = ['meal', 'ate', 'eaten', 'food', 'breakfast', 'lunch', 'dinner', 'snack']
        return any(keyword in message for keyword in keywords)

    def _is_nutrition_query(self, message):
        keywords = ['calorie', 'protein', 'carb', 'fat', 'fiber', 'nutrition', 'nutrient']
        return any(keyword in message for keyword in keywords)

    def _is_medication_query(self, message):
        keywords = ['medication', 'medicine', 'drug', 'pill', 'taking']
        return any(keyword in message for keyword in keywords)

    def _is_goal_query(self, message):
        keywords = ['goal', 'target', 'should', 'progress', 'meeting']
        return any(keyword in message for keyword in keywords)

    def _is_log_meal_intent(self, message):
        keywords = ['log', 'add meal', 'record meal', 'ate', 'had']
        return any(keyword in message for keyword in keywords) and any(word in message for word in ['calorie', 'kcal', 'protein'])

    def _is_add_medication_intent(self, message):
        keywords = ['add medication', 'new medication', 'start taking', 'prescribed']
        return any(keyword in message for keyword in keywords)

    # Query handlers
    def _handle_meal_query(self, message):
        """Handle queries about meals"""
        if 'today' in message:
            return self._get_today_meals()
        elif 'yesterday' in message:
            return self._get_yesterday_meals()
        elif 'week' in message or 'this week' in message:
            return self._get_week_meals()
        elif 'list' in message or 'show' in message:
            return self._get_recent_meals()
        else:
            return self._get_today_meals()

    def _handle_nutrition_query(self, message):
        """Handle queries about nutrition"""
        if 'today' in message:
            return self._get_today_nutrition()
        elif 'yesterday' in message:
            return self._get_yesterday_nutrition()
        elif 'week' in message:
            return self._get_week_nutrition()
        elif 'month' in message:
            return self._get_month_nutrition()
        else:
            return self._get_today_nutrition()

    def _handle_medication_query(self, message):
        """Handle queries about medications"""
        medications = Medication.objects.filter(user=self.user, is_active=True)

        if not medications.exists():
            return "You don't have any active medications recorded. Would you like to add one?"

        response = f"You are currently taking {medications.count()} medication(s):\n\n"
        for med in medications:
            response += f"• **{med.drug_name}** - {med.dosage}, {med.get_frequency_display()}\n"
            if med.notes:
                response += f"  Notes: {med.notes}\n"

        return response

    def _handle_goal_query(self, message):
        """Handle queries about health goals"""
        today = timezone.now().date()
        meals_today = Meal.objects.filter(user=self.user, date=today)

        totals = meals_today.aggregate(
            total_calories=Sum('calories'),
            total_protein=Sum('protein'),
            total_carbs=Sum('carbs'),
            total_fat=Sum('fat'),
            total_fiber=Sum('fiber')
        )

        response = f"**Your Daily Goals vs Progress (Today)**\n\n"

        goals = [
            ('Calories', totals['total_calories'] or 0, self.user.daily_calorie_goal),
            ('Protein', totals['total_protein'] or 0, self.user.daily_protein_goal),
            ('Carbs', totals['total_carbs'] or 0, self.user.daily_carbs_goal),
            ('Fat', totals['total_fat'] or 0, self.user.daily_fat_goal),
            ('Fiber', totals['total_fiber'] or 0, self.user.daily_fiber_goal),
        ]

        for name, actual, goal in goals:
            percentage = (actual / goal * 100) if goal > 0 else 0
            status = "✅" if percentage >= 90 else "⚠️" if percentage >= 70 else "❌"
            unit = "kcal" if name == "Calories" else "g"
            response += f"{status} **{name}**: {actual:.1f}{unit} / {goal:.1f}{unit} ({percentage:.0f}%)\n"

        return response

    def _handle_log_meal_intent(self, message):
        """Guide user to log a meal"""
        return ("I can help you log a meal! Please use the meal logging endpoint:\n\n"
                "**POST /api/meals/**\n"
                "```json\n"
                "{\n"
                '  "meal_name": "Chicken Salad",\n'
                '  "meal_time": "lunch",\n'
                '  "calories": 350,\n'
                '  "protein": 30,\n'
                '  "carbs": 20,\n'
                '  "fat": 15,\n'
                '  "fiber": 5\n'
                "}\n"
                "```")

    def _handle_add_medication_intent(self, message):
        """Guide user to add medication"""
        return ("I can help you add a medication! Please use the medication endpoint:\n\n"
                "**POST /api/medications/**\n"
                "```json\n"
                "{\n"
                '  "drug_name": "Metformin",\n'
                '  "dosage": "500mg",\n'
                '  "frequency": "twice_daily"\n'
                "}\n"
                "```")

    def _handle_general_query(self, message):
        """Handle general queries"""
        if any(word in message for word in ['hello', 'hi', 'hey']):
            return f"Hello {self.user.name}! I'm your health assistant. I can help you track meals, medications, and monitor your nutrition goals. What would you like to know?"
        elif 'help' in message:
            return self._get_help_message()
        else:
            return ("I can help you with:\n"
                    "• Tracking your meals and nutrition\n"
                    "• Managing medications\n"
                    "• Monitoring your health goals\n"
                    "• Viewing your progress\n\n"
                    "Try asking me things like:\n"
                    "- 'What did I eat today?'\n"
                    "- 'How much protein have I consumed this week?'\n"
                    "- 'Show me my medications'\n"
                    "- 'Am I meeting my goals?'")

    # Data retrieval methods
    def _get_today_meals(self):
        """Get today's meals"""
        today = timezone.now().date()
        meals = Meal.objects.filter(user=self.user, date=today)

        if not meals.exists():
            return "You haven't logged any meals today yet. Would you like to add one?"

        response = f"**Today's Meals ({today})**\n\n"
        total_calories = 0

        for meal in meals:
            response += f"**{meal.get_meal_time_display()}**: {meal.meal_name}\n"
            response += f"  • Calories: {meal.calories:.0f} kcal\n"
            response += f"  • Protein: {meal.protein:.1f}g, Carbs: {meal.carbs:.1f}g, Fat: {meal.fat:.1f}g\n\n"
            total_calories += meal.calories

        response += f"**Total Calories Today**: {total_calories:.0f} kcal"
        return response

    def _get_yesterday_meals(self):
        """Get yesterday's meals"""
        yesterday = timezone.now().date() - timedelta(days=1)
        meals = Meal.objects.filter(user=self.user, date=yesterday)

        if not meals.exists():
            return f"You didn't log any meals on {yesterday}."

        response = f"**Yesterday's Meals ({yesterday})**\n\n"
        for meal in meals:
            response += f"**{meal.get_meal_time_display()}**: {meal.meal_name} ({meal.calories:.0f} kcal)\n"

        return response

    def _get_week_meals(self):
        """Get this week's meals"""
        week_ago = timezone.now().date() - timedelta(days=7)
        meals = Meal.objects.filter(user=self.user, date__gte=week_ago)

        if not meals.exists():
            return "You haven't logged any meals in the past week."

        count = meals.count()
        response = f"**This Week's Summary**\n\n"
        response += f"You logged {count} meal(s) in the past 7 days.\n\n"

        # Group by date
        dates = meals.values_list('date', flat=True).distinct().order_by('-date')
        for date in dates[:5]:  # Show last 5 days
            day_meals = meals.filter(date=date)
            day_cals = sum(m.calories for m in day_meals)
            response += f"**{date}**: {day_meals.count()} meals, {day_cals:.0f} kcal\n"

        return response

    def _get_recent_meals(self):
        """Get recent meals"""
        meals = Meal.objects.filter(user=self.user)[:10]

        if not meals.exists():
            return "You haven't logged any meals yet."

        response = "**Your Recent Meals**\n\n"
        for meal in meals:
            response += f"• {meal.date} - {meal.meal_name} ({meal.calories:.0f} kcal)\n"

        return response

    def _get_today_nutrition(self):
        """Get today's nutrition totals"""
        today = timezone.now().date()
        meals = Meal.objects.filter(user=self.user, date=today)

        if not meals.exists():
            return "You haven't logged any meals today yet."

        totals = meals.aggregate(
            calories=Sum('calories'),
            protein=Sum('protein'),
            carbs=Sum('carbs'),
            fat=Sum('fat'),
            fiber=Sum('fiber')
        )

        response = f"**Today's Nutrition Summary**\n\n"
        response += f"• **Calories**: {totals['calories']:.0f} kcal\n"
        response += f"• **Protein**: {totals['protein']:.1f}g\n"
        response += f"• **Carbs**: {totals['carbs']:.1f}g\n"
        response += f"• **Fat**: {totals['fat']:.1f}g\n"
        response += f"• **Fiber**: {totals['fiber']:.1f}g\n"

        return response

    def _get_yesterday_nutrition(self):
        """Get yesterday's nutrition"""
        yesterday = timezone.now().date() - timedelta(days=1)
        meals = Meal.objects.filter(user=self.user, date=yesterday)

        if not meals.exists():
            return f"No meals logged for {yesterday}."

        totals = meals.aggregate(
            calories=Sum('calories'),
            protein=Sum('protein')
        )

        return f"**Yesterday ({yesterday})**\n• Calories: {totals['calories']:.0f} kcal\n• Protein: {totals['protein']:.1f}g"

    def _get_week_nutrition(self):
        """Get week's nutrition"""
        week_ago = timezone.now().date() - timedelta(days=7)
        meals = Meal.objects.filter(user=self.user, date__gte=week_ago)

        if not meals.exists():
            return "No meals logged this week."

        totals = meals.aggregate(
            calories=Sum('calories'),
            protein=Sum('protein'),
            carbs=Sum('carbs'),
            fat=Sum('fat'),
            fiber=Sum('fiber')
        )

        avg_calories = totals['calories'] / 7 if totals['calories'] else 0

        response = f"**This Week's Nutrition**\n\n"
        response += f"• **Total Calories**: {totals['calories']:.0f} kcal\n"
        response += f"• **Avg per Day**: {avg_calories:.0f} kcal\n"
        response += f"• **Total Protein**: {totals['protein']:.1f}g\n"
        response += f"• **Total Carbs**: {totals['carbs']:.1f}g\n"

        return response

    def _get_month_nutrition(self):
        """Get month's nutrition"""
        month_ago = timezone.now().date() - timedelta(days=30)
        meals = Meal.objects.filter(user=self.user, date__gte=month_ago)

        if not meals.exists():
            return "No meals logged this month."

        totals = meals.aggregate(
            calories=Sum('calories'),
            protein=Sum('protein')
        )

        avg_calories = totals['calories'] / 30 if totals['calories'] else 0

        response = f"**This Month's Nutrition**\n\n"
        response += f"• **Total Calories**: {totals['calories']:.0f} kcal\n"
        response += f"• **Avg per Day**: {avg_calories:.0f} kcal\n"
        response += f"• **Total Protein**: {totals['protein']:.1f}g\n"

        return response

    def _get_help_message(self):
        """Get help message"""
        return """**I can help you with:**

📊 **Nutrition Tracking**
- "What did I eat today?"
- "How many calories have I consumed this week?"
- "Show me my protein intake"

💊 **Medication Management**
- "Show my medications"
- "What medications am I taking?"

🎯 **Goal Tracking**
- "Am I meeting my goals?"
- "Show my progress"

📝 **Data Entry**
- Use the API endpoints to log meals and medications

Just ask me in plain English and I'll help you track your health!"""
