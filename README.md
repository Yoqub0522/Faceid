FaceID MVT Django project
------------------------

Minimal FaceID-based attendance system.

Run:
1. python -m venv venv
2. source venv/bin/activate   # or venv\Scripts\activate on Windows
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py createsuperuser
6. python manage.py runserver

Visit:
- /enroll/ to create employee
- /enroll/<employee_id>/ to upload photos for encoding
- /capture/ to use webcam for check-in/out
