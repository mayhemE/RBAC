#!/usr/bin/env bash

set -e


if [-f "manage.py"]; then
    flask db migrate || echo "Migrations failed"
fi 

python - <<'PY'
from app import db, app 

with app.app_context():
        db.create_all()

PY

exec gunicorn "app:app" --bind 0.0.0.0:&port --workers 3
