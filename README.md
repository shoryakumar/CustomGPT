## Biorhyme Health Custom GPT - Proof of Concept

A simplified demonstration of a health chatbot that can:
- Answer questions about meals and nutrition from a database
- Perform CRUD operations on meals and medications
- Track nutrition goals and progress
- Provide personalized health insights

**No Authentication Required** - This is a demo POC for testing purposes.

---

## Features

### 🤖 Intelligent Chatbot
- Natural language understanding
- Database-driven responses
- Context-aware conversations
- Tracks chat history

### 🍽️ Meal Tracking
- Log meals with complete nutrition info
- View meals by date range
- Update and delete entries
- Calculate nutrition totals

### 💊 Medication Management
- Track medications and dosages
- Manage frequency and notes
- View active medications
- Full CRUD operations

### 📊 Health Analytics
- Daily/weekly/monthly summaries
- Progress vs goals tracking
- Nutrition breakdowns
- Personalized insights

---

## Quick Start

### 1. Install Dependencies

```bash
cd tryCustomGPT
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python manage.py migrate
```

### 3. Load Demo Data

```bash
python manage.py load_demo_data
```

This creates:
- Demo user profile
- 15 sample meals over 5 days
- 3 sample medications
- Health goals and conditions

### 4. Run Server

```bash
python manage.py runserver
```

Server will start at: http://localhost:8000

---

## API Endpoints

### 🏥 Health Check
```bash
GET /api/health/
```

Response:
```json
{
  "status": "ok",
  "message": "Biorhyme Health Chatbot Demo is running",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### 💬 Chat with Bot

```bash
POST /api/chat/
Content-Type: application/json

{
  "message": "What did I eat today?"
}
```

Response:
```json
{
  "message": "What did I eat today?",
  "response": "**Today's Meals (2024-01-15)**\n\n**Breakfast**: Oatmeal with Berries\n  • Calories: 350 kcal\n  • Protein: 12.0g, Carbs: 58.0g, Fat: 8.0g\n\n...",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

### 🍽️ Meal Operations

#### List Meals
```bash
GET /api/meals/?days=7
```

Response:
```json
{
  "count": 15,
  "meals": [
    {
      "id": 1,
      "meal_name": "Oatmeal with Berries",
      "meal_time": "breakfast",
      "calories": 350,
      "protein": 12,
      "carbs": 58,
      "fat": 8,
      "fiber": 8,
      "date": "2024-01-15",
      "notes": "",
      "created_at": "2024-01-15T08:30:00Z"
    },
    ...
  ],
  "totals": {
    "total_calories": 6240,
    "total_protein": 398,
    "total_carbs": 668,
    "total_fat": 198,
    "total_fiber": 94
  }
}
```

#### Create Meal
```bash
POST /api/meals/
Content-Type: application/json

{
  "meal_name": "Chicken Salad",
  "meal_time": "lunch",
  "calories": 420,
  "protein": 38,
  "carbs": 25,
  "fat": 18,
  "fiber": 6,
  "notes": "With olive oil dressing"
}
```

Response:
```json
{
  "success": true,
  "message": "Meal logged successfully",
  "meal": {
    "id": 16,
    "meal_name": "Chicken Salad",
    ...
  }
}
```

#### Get Meal Details
```bash
GET /api/meals/1/
```

#### Update Meal
```bash
PUT /api/meals/1/
Content-Type: application/json

{
  "calories": 380
}
```

#### Delete Meal
```bash
DELETE /api/meals/1/
```

### 💊 Medication Operations

#### List Medications
```bash
GET /api/medications/
```

Response:
```json
{
  "count": 3,
  "medications": [
    {
      "id": 1,
      "drug_name": "Metformin",
      "dosage": "500mg",
      "frequency": "twice_daily",
      "started_date": "2023-12-15",
      "notes": "Take with meals",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z"
    },
    ...
  ]
}
```

#### Add Medication
```bash
POST /api/medications/
Content-Type: application/json

{
  "drug_name": "Aspirin",
  "dosage": "81mg",
  "frequency": "once_daily",
  "notes": "Baby aspirin for heart health"
}
```

#### Update Medication
```bash
PUT /api/medications/1/
Content-Type: application/json

{
  "dosage": "1000mg"
}
```

#### Delete Medication
```bash
DELETE /api/medications/1/
```

### 📊 Summary & Analytics

```bash
GET /api/summary/?period=today
GET /api/summary/?period=week
GET /api/summary/?period=month
```

Response:
```json
{
  "period": "week",
  "date_range": {
    "from": "2024-01-08",
    "to": "2024-01-15",
    "days": 8
  },
  "meals_logged": 15,
  "totals": {
    "total_calories": 6240,
    "total_protein": 398,
    "total_carbs": 668,
    "total_fat": 198,
    "total_fiber": 94
  },
  "daily_averages": {
    "avg_calories": 780,
    "avg_protein": 49.75,
    "avg_carbs": 83.5,
    "avg_fat": 24.75,
    "avg_fiber": 11.75
  },
  "goals": {
    "calories": 2000,
    "protein": 150,
    "carbs": 250,
    "fat": 65,
    "fiber": 30
  },
  "progress_percentage": {
    "calories": 39.0,
    "protein": 33.2,
    "carbs": 33.4,
    "fat": 38.1,
    "fiber": 39.2
  }
}
```

### 📝 Chat History

```bash
GET /api/chat/history/?limit=10
```

### 👤 User Profile

```bash
GET /api/profile/
```

Response:
```json
{
  "id": 1,
  "email": "demo@biorhyme.health",
  "name": "Demo User",
  "age": 30,
  "daily_calorie_goal": 2000,
  "daily_protein_goal": 150,
  "daily_carbs_goal": 250,
  "daily_fat_goal": 65,
  "daily_fiber_goal": 30,
  "health_conditions": ["Type 2 Diabetes", "Hypertension"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 🔄 Reset Demo

```bash
POST /api/reset/
```

Deletes all meals, medications, and chat history. Use `load_demo_data` command to reload.

---

## Testing the Chatbot

### Example Questions

Try these natural language queries with the chatbot:

#### Meal Queries
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me meals from yesterday"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat this week?"}'
```

#### Nutrition Queries
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How many calories have I consumed today?"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my protein intake for this week"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "How much fiber did I eat this month?"}'
```

#### Goal Tracking
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Am I meeting my nutrition goals?"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my progress"}'
```

#### Medication Queries
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What medications am I taking?"}'

curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my medications"}'
```

#### General
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Help"}'
```

---

## Using with Postman / Insomnia

### Import Collection

1. Create a new collection
2. Set base URL: `http://localhost:8000`
3. Add requests for each endpoint

### Sample Requests

**Chat:**
- Method: POST
- URL: `{{base_url}}/api/chat/`
- Body (JSON):
  ```json
  {
    "message": "What did I eat today?"
  }
  ```

**Create Meal:**
- Method: POST
- URL: `{{base_url}}/api/meals/`
- Body (JSON):
  ```json
  {
    "meal_name": "Grilled Salmon",
    "meal_time": "dinner",
    "calories": 450,
    "protein": 40,
    "carbs": 12,
    "fat": 25,
    "fiber": 2
  }
  ```

---

## Database Schema

### UserProfile
- email (unique)
- name
- age
- daily nutrition goals (calories, protein, carbs, fat, fiber)
- health_conditions (JSON)

### Meal
- user (FK to UserProfile)
- meal_name
- meal_time (breakfast, lunch, dinner, snack)
- nutrition (calories, protein, carbs, fat, fiber)
- date
- notes

### Medication
- user (FK to UserProfile)
- drug_name
- dosage
- frequency
- started_date
- notes
- is_active

### ChatMessage
- user (FK to UserProfile)
- user_message
- bot_response
- query_type
- created_at

---

## Django Admin

Access admin panel at: http://localhost:8000/admin/

Create superuser:
```bash
python manage.py createsuperuser
```

Features:
- View all meals, medications, chat messages
- Edit data directly
- Filter and search
- Export data

---

## How It Works

### Chatbot Logic

The chatbot uses a simple rule-based system:

1. **Intent Detection**: Analyzes keywords to determine user intent
   - Meal queries: "ate", "food", "meal"
   - Nutrition queries: "calories", "protein", "carbs"
   - Medication queries: "medication", "drug", "pill"
   - Goal queries: "goal", "progress", "meeting"

2. **Database Query**: Retrieves relevant data based on intent
   - Filters by user, date range
   - Aggregates nutrition totals
   - Calculates averages and progress

3. **Response Generation**: Formats data into natural language
   - Uses Markdown formatting
   - Includes emojis for visual appeal
   - Provides context and recommendations

### Example Flow

```
User: "What did I eat today?"
  ↓
Intent Detection → Meal Query (today)
  ↓
Database Query → Meal.objects.filter(user=user, date=today)
  ↓
Response Generation → Format meals with nutrition info
  ↓
Response: "**Today's Meals (2024-01-15)**..."
```

---

## Customization

### Adding New Intents

Edit `health_chatbot/chatbot.py`:

```python
def _is_custom_query(self, message):
    keywords = ['custom', 'special']
    return any(keyword in message for keyword in keywords)

def _handle_custom_query(self, message):
    # Your custom logic
    return "Custom response"
```

### Modifying Goals

Update in `load_demo_data` command or via Django admin.

### Changing Response Format

Edit the response generation methods in `chatbot.py`.

---

## Production Considerations

This is a **POC/Demo** and lacks:

❌ Authentication/Authorization
❌ Rate limiting
❌ Input validation/sanitization
❌ Proper error handling
❌ Security measures
❌ Performance optimization
❌ AI/ML models (uses rule-based logic)

For production:

✅ Add proper authentication (JWT, OAuth)
✅ Implement rate limiting
✅ Add input validation
✅ Use PostgreSQL instead of SQLite
✅ Add caching (Redis)
✅ Implement proper logging
✅ Add monitoring (Sentry, DataDog)
✅ Use real AI models (OpenAI, Claude)
✅ Add comprehensive tests
✅ Deploy with Docker/Kubernetes

---

## Troubleshooting

### Port Already in Use

```bash
python manage.py runserver 8001
```

### Database Locked

```bash
rm demo_db.sqlite3
python manage.py migrate
python manage.py load_demo_data
```

### Module Not Found

```bash
pip install -r requirements.txt
```

### CORS Errors

CORS is disabled in this demo. For production, configure properly.

---

## Demo Video Script

### 1. Show Health Check
```bash
curl http://localhost:8000/api/health/
```

### 2. Ask About Today's Meals
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'
```

### 3. Check Goals
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Am I meeting my goals?"}'
```

### 4. Add a New Meal
```bash
curl -X POST http://localhost:8000/api/meals/ \
  -H "Content-Type: application/json" \
  -d '{
    "meal_name": "Protein Shake",
    "meal_time": "snack",
    "calories": 200,
    "protein": 25,
    "carbs": 15,
    "fat": 5,
    "fiber": 2
  }'
```

### 5. Ask Again
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'
```
Now shows the newly added meal!

### 6. Check Medications
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What medications am I taking?"}'
```

### 7. View Summary
```bash
curl http://localhost:8000/api/summary/?period=week
```

---

## Next Steps

1. **Integrate with AI Models**
   - OpenAI GPT-4
   - Anthropic Claude
   - AWS Bedrock

2. **Add More Features**
   - Image recognition for food
   - Barcode scanning
   - Recipe suggestions
   - Drug interaction checks
   - Evidence-based research

3. **Improve Chatbot**
   - Context awareness
   - Multi-turn conversations
   - Entity extraction
   - Sentiment analysis

4. **Production Ready**
   - Authentication
   - Testing
   - CI/CD
   - Monitoring

---

## Contact

For questions or issues, please refer to the main project documentation.

---

## License

Demo/POC - For evaluation purposes only.
