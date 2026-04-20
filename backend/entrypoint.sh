#!/bin/bash
set -e

echo "⏳ Waiting for database..."
python << END
import time, os, psycopg2
for i in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ.get('POSTGRES_DB', 'unimap_db'),
            user=os.environ.get('POSTGRES_USER', 'unimap_user'),
            password=os.environ.get('POSTGRES_PASSWORD', 'unimap_pass'),
            host=os.environ.get('POSTGRES_HOST', 'db'),
            port=os.environ.get('POSTGRES_PORT', '5432'),
        )
        print("✅ Database ready")
        break
    except psycopg2.OperationalError:
        print(f"  attempt {i+1}/30...")
        time.sleep(2)
else:
    print("❌ Database not available after 60s")
    exit(1)
END

echo "🔄 Running migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn..."
exec gunicorn unimap_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --access-logfile - \
    --error-logfile -
