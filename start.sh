#!/usr/bin/env bash
set -e

echo "Running migrations (if available)..."
if [ ! -f db.sqlite3 ]; then
  flask db upgrade
fi


echo "Ensuring database tables exist..."
python - <<'PY'
from app import db, app
with app.app_context():
    db.create_all()
PY

echo "Starting gunicorn..."
exec gunicorn "app:app" --bind 0.0.0.0:$PORT --workers 3
