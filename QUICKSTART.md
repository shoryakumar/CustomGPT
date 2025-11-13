# Quick Start Guide

Get the demo running in 3 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- PostgreSQL RDS access (credentials already in `.env` file)

## Setup (2 minutes)

### Option 1: Automatic Setup (macOS/Linux)

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup (Windows/All)

```bash
# 1. Check .env file exists (with RDS credentials)
cat .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup PostgreSQL database
python manage.py migrate

# 4. Load demo data
python manage.py load_demo_data
```

**Database:** PostgreSQL on AWS RDS
- Host: `ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com`
- Database: `postgres`
- Credentials in `.env` file

## Run (30 seconds)

```bash
python manage.py runserver
```

Visit: http://localhost:8000

## Test (1 minute)

### Option 1: Use Test Script (macOS/Linux)

```bash
chmod +x test_api.sh
./test_api.sh
```

### Option 2: Manual Test

```bash
# Test chatbot
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'

# Get meal summary
curl http://localhost:8000/api/summary/?period=today
```

## Example Interactions

### 1. Ask about meals
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'
```

**Response:**
```
Today's Meals (2024-01-15)

Breakfast: Oatmeal with Berries
  • Calories: 350 kcal
  • Protein: 12.0g, Carbs: 58.0g, Fat: 8.0g

Lunch: Grilled Chicken Salad
  • Calories: 420 kcal
  • Protein: 38.0g, Carbs: 25.0g, Fat: 18.0g
...
```

### 2. Check nutrition goals
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Am I meeting my goals?"}'
```

### 3. View medications
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What medications am I taking?"}'
```

### 4. Add a new meal
```bash
curl -X POST http://localhost:8000/api/meals/ \
  -H "Content-Type: application/json" \
  -d '{
    "meal_name": "Grilled Salmon",
    "meal_time": "dinner",
    "calories": 450,
    "protein": 40,
    "carbs": 12,
    "fat": 25,
    "fiber": 2
  }'
```

## API Endpoints Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health/` | GET | Health check |
| `/api/chat/` | POST | Chat with bot |
| `/api/meals/` | GET, POST | List/create meals |
| `/api/meals/<id>/` | GET, PUT, DELETE | Meal CRUD |
| `/api/medications/` | GET, POST | List/create meds |
| `/api/medications/<id>/` | GET, PUT, DELETE | Med CRUD |
| `/api/summary/` | GET | Nutrition summary |
| `/api/profile/` | GET | User profile |

## What's in the Demo?

- ✅ **15 sample meals** across 5 days
- ✅ **3 medications** with dosages
- ✅ **Nutrition goals** (2000 cal, 150g protein, etc.)
- ✅ **Health conditions** (Type 2 Diabetes, Hypertension)
- ✅ **Chat history** tracking
- ✅ **Full CRUD** on all entities

## Next Steps

1. ✅ Test the API endpoints
2. ✅ Try chatbot queries
3. ✅ Add/update/delete data
4. ✅ Check summaries and progress
5. 📖 Read full [README.md](README.md) for details

## Troubleshooting

**Issue**: Port 8000 already in use
```bash
python manage.py runserver 8001
```

**Issue**: Module not found
```bash
pip install -r requirements.txt
```

**Issue**: Want to start fresh
```bash
python manage.py flush  # Clear PostgreSQL data
python manage.py migrate
python manage.py load_demo_data
```

**Issue**: Database connection error
- Check RDS instance is running
- Verify credentials in `.env` file
- See [ENV_SETUP.md](ENV_SETUP.md) for detailed troubleshooting

## Support

- Full documentation: [README.md](README.md)
- Environment setup: [ENV_SETUP.md](ENV_SETUP.md)
- Database schema: See models.py
- Chatbot logic: See chatbot.py

Happy testing! 🎉
