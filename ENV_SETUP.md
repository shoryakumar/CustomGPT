# Environment Setup Guide

This guide explains how to set up the environment for the Custom GPT Demo with PostgreSQL RDS.

---

## Database Configuration

This project uses **PostgreSQL on AWS RDS** instead of SQLite.

### Connection Details

The database credentials are stored in the `.env` file:

```
RDS_HOSTNAME=ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB_NAME=postgres
RDS_USERNAME=postgres
RDS_PASSWORD=postgres
```

---

## Setup Steps

### 1. Copy Environment File

The `.env` file contains your database credentials:

```bash
# Already created for you with RDS credentials
cat .env
```

If you need to change credentials, edit `.env`:

```bash
nano .env
# or
vim .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Django 4.2.11
- Django REST Framework
- django-cors-headers
- **psycopg2-binary** (PostgreSQL adapter)
- **python-decouple** (environment management)

### 3. Verify Database Connection

Test if you can connect to the RDS instance:

```bash
python3 manage.py check
```

If successful, you should see:
```
System check identified no issues (0 silenced).
```

### 4. Run Migrations

Create the database tables:

```bash
python3 manage.py migrate
```

This will create:
- `user_profiles` table
- `meals` table
- `medications` table
- `chat_messages` table
- Django system tables

### 5. Load Demo Data

```bash
python3 manage.py load_demo_data
```

This creates:
- 1 demo user profile
- 15 sample meals
- 3 medications

### 6. Run Server

```bash
python3 manage.py runserver
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `RDS_HOSTNAME` | PostgreSQL hostname | `ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com` |
| `RDS_PORT` | Database port | `5432` |
| `RDS_DB_NAME` | Database name | `postgres` |
| `RDS_USERNAME` | Database user | `postgres` |
| `RDS_PASSWORD` | Database password | `postgres` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `CORS_ALLOW_ALL_ORIGINS` | Allow all CORS | `True` |

---

## Database Schema

After running migrations, the following tables are created:

### user_profiles
```sql
id, email, name, age,
daily_calorie_goal, daily_protein_goal, daily_carbs_goal, daily_fat_goal, daily_fiber_goal,
health_conditions (JSONB), created_at
```

### meals
```sql
id, user_id, meal_name, meal_time,
calories, protein, carbs, fat, fiber,
date, notes, created_at
```

### medications
```sql
id, user_id, drug_name, dosage, frequency,
started_date, notes, is_active, created_at, updated_at
```

### chat_messages
```sql
id, user_id, user_message, bot_response,
query_type, created_at
```

---

## Connecting to the Database Directly

### Using psql (PostgreSQL CLI)

```bash
psql -h ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com \
     -p 5432 \
     -U postgres \
     -d postgres
```

Password: `postgres`

### Using Python

```python
import psycopg2

conn = psycopg2.connect(
    host='ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com',
    port=5432,
    database='postgres',
    user='postgres',
    password='postgres'
)
cursor = conn.cursor()
cursor.execute("SELECT * FROM user_profiles;")
print(cursor.fetchall())
```

### Using Django Shell

```bash
python3 manage.py shell
```

```python
from health_chatbot.models import UserProfile, Meal, Medication

# Get demo user
user = UserProfile.objects.get(email='demo@biorhyme.health')
print(user.name)

# Get meals
meals = Meal.objects.filter(user=user)
print(f"Total meals: {meals.count()}")

# Get medications
meds = Medication.objects.filter(user=user)
for med in meds:
    print(f"{med.drug_name} - {med.dosage}")
```

---

## Troubleshooting

### Issue: Cannot connect to database

**Error:**
```
django.db.utils.OperationalError: could not connect to server
```

**Solutions:**
1. Check if RDS instance is running
2. Verify security group allows your IP
3. Check credentials in `.env` file
4. Test connection with psql

```bash
# Test connection
psql -h ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com -U postgres -d postgres
```

### Issue: Module 'psycopg2' not found

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: Permission denied

**Error:**
```
permission denied for database
```

**Solutions:**
1. Verify username/password are correct
2. Check user has CREATE/ALTER permissions
3. Try with superuser credentials

### Issue: Database does not exist

**Error:**
```
database "postgres" does not exist
```

**Solution:**
```bash
# Connect to default database and create
psql -h ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com -U postgres
CREATE DATABASE postgres;
```

Or change `RDS_DB_NAME` in `.env` to an existing database.

### Issue: Port not accessible

**Solutions:**
1. Check AWS Security Group allows inbound on port 5432
2. Check VPC settings
3. Verify RDS instance is publicly accessible (if needed)

---

## Security Notes

### Development vs Production

**Current Setup (Demo):**
- ❌ Credentials in `.env` file
- ❌ Simple password
- ❌ DEBUG=True
- ❌ ALLOWED_HOSTS='*'
- ❌ CORS allows all origins

**Production Setup Should Have:**
- ✅ Secrets stored in AWS Secrets Manager
- ✅ Strong passwords
- ✅ DEBUG=False
- ✅ Specific ALLOWED_HOSTS
- ✅ Restricted CORS origins
- ✅ SSL/TLS connections
- ✅ Connection pooling
- ✅ Read replicas for scaling

### Securing .env File

**IMPORTANT:** Never commit `.env` to version control!

```bash
# Already in .gitignore
echo ".env" >> .gitignore
```

For production, use:
- AWS Secrets Manager
- Environment variables in deployment
- Encrypted configuration

---

## Database Management

### Backup Database

```bash
# Dump schema and data
pg_dump -h ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com \
        -U postgres \
        -d postgres \
        -F c \
        -f backup.dump

# Or just data
python3 manage.py dumpdata > data_backup.json
```

### Restore Database

```bash
# From dump file
pg_restore -h ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com \
           -U postgres \
           -d postgres \
           backup.dump

# From Django JSON
python3 manage.py loaddata data_backup.json
```

### Reset Database

```bash
# Drop all tables and recreate
python3 manage.py flush

# Or reset migrations
python3 manage.py migrate health_chatbot zero
python3 manage.py migrate

# Reload demo data
python3 manage.py load_demo_data
```

---

## Performance Optimization

### Connection Pooling

For production, add to `settings.py`:

```python
DATABASES = {
    'default': {
        # ... existing config ...
        'CONN_MAX_AGE': 600,  # 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

### Indexing

Common queries should have indexes. Already included in models:

```python
# In models.py
class Meta:
    indexes = [
        models.Index(fields=['user', 'date']),
        models.Index(fields=['created_at']),
    ]
```

### Query Optimization

Use `select_related` and `prefetch_related`:

```python
# Good - single query
meals = Meal.objects.select_related('user').all()

# Bad - N+1 queries
meals = Meal.objects.all()
for meal in meals:
    print(meal.user.name)  # Extra query per meal
```

---

## Monitoring

### Check Database Status

```bash
# Django command
python3 manage.py dbshell

# Inside psql
\dt  -- List tables
\d user_profiles  -- Describe table
SELECT COUNT(*) FROM meals;
SELECT COUNT(*) FROM medications;
```

### Check Connection Pool

```python
from django.db import connection
print(connection.queries)  # Show executed queries (DEBUG=True only)
```

### Log Queries

In `settings.py` for development:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Next Steps

1. ✅ Environment configured
2. ✅ Database connected
3. ✅ Migrations run
4. ✅ Demo data loaded
5. 🚀 Ready to use!

Run the server:
```bash
python3 manage.py runserver
```

Test the API:
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'
```

---

## Resources

- [Django Database Documentation](https://docs.djangoproject.com/en/4.2/ref/databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [AWS RDS Documentation](https://docs.aws.amazon.com/rds/)
- [python-decouple Documentation](https://pypi.org/project/python-decouple/)
