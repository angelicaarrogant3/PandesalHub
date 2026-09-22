#!/usr/bin/env bash
set -o errexit  # exit if any command fails

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Running pre-migration fix..."
python pre_migrate.py

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Creating superuser (if not exists)..."
python manage.py createsuperuser --noinput || true

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Build complete!"
