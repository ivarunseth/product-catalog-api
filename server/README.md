## Backend (Flask)

Quickstart:

1. Create virtualenv and install:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Initialize DB (sqlite used by default):
   ```
   export FLASK_APP=app.py
   flask db init  # optional; migrations not included in archive
   ```
3. Seed data:
   ```
   python seed.py
   ```
4. Run:
   ```
   flask run
   ```
The backend exposes:
- GET /api/products/search?q=&page=&limit=
- GET /api/products/<slug>
- POST /api/admin/products  (simple create)
