# attendance/apps.py
from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    verbose_name = 'Yuz Tanish Davomat Tizimi'

    def ready(self):
        """Django ishga tushganda signal larni yuklash"""
        try:
            # Signal larni import qilish
            from . import signals
            print("Signals muvaffaqiyatli yuklandi")
        except ImportError as e:
            print(f"Signals yuklashda xatolik: {e}")