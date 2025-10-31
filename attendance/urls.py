# attendance/urls.py (YANGILANGAN)
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Asosiy sahifalar
    path('', views.index, name='index'),
    path('enroll/', views.enroll, name='enroll'),
    path('enroll/<uuid:employee_id>/', views.enroll_images, name='enroll_images'),
    path('capture/', views.capture_page, name='capture'),
    path('report/', views.report, name='report'),

    # API endpoints
    path('api/recognize/', views.recognize_api, name='recognize_api'),
    path('process_attendance/', views.recognize_api, name='process_attendance'),  # ✅ QO'SHILDI
    path('api/encoding/<uuid:encoding_id>/delete/', views.delete_encoding, name='delete_encoding'),
    path('api/encoding/<uuid:encoding_id>/primary/', views.set_primary_encoding, name='set_primary_encoding'),
]