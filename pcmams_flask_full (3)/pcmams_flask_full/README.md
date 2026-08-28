
PCMAMS - Full Flask version
===========================

How to run locally
------------------
1. Create a virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate   (on Windows: venv\Scripts\activate)

2. Install requirements:
   pip install -r requirements.txt

3. Initialize database with sample data:
   python init_db.py

4. Run the app:
   python run.py

Default sample accounts:
 - alice / pass  (adopter)
 - bob / pass    (vet)
 - admin / admin (admin)

Project layout
--------------
pcmams/                - Flask package
  __init__.py
  models.py
  auth.py
  main.py
  api.py
  templates/           - Jinja2 templates
  static/              - CSS and product_images
run.py                 - entrypoint
init_db.py             - initializes sqlite DB with sample data
requirements.txt

Notes
-----
- SECRET_KEY is set via environment variable PCMAMS_SECRET (defaults to a dev value).
- This is a starting skeleton: you can extend CRUD, file uploads, validations, and role-based pages.
