# attendance/signals.py
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

@receiver(post_delete, sender='attendance.Employee')
def auto_delete_photo_on_delete(sender, instance, **kwargs):
    """
    Xodim o'chirilganda uning rasmini fayl tizimidan o'chiradi
    """
    if instance.photo:
        if os.path.isfile(instance.photo.path):
            try:
                os.remove(instance.photo.path)
                print(f"Rasm o'chirildi: {instance.photo.path}")
            except Exception as e:
                print(f"Rasm o'chirishda xatolik: {e}")

@receiver(pre_save, sender='attendance.Employee')
def auto_delete_photo_on_change(sender, instance, **kwargs):
    """
    Xodim yangilanganda eski rasmini o'chiradi
    """
    if not instance.pk:
        return False

    try:
        from .models import Employee
        old_employee = Employee.objects.get(pk=instance.pk)
        old_photo = old_employee.photo
    except Employee.DoesNotExist:
        return False

    new_photo = instance.photo
    if old_photo and old_photo != new_photo:
        if os.path.isfile(old_photo.path):
            try:
                os.remove(old_photo.path)
                print(f"Eski rasm o'chirildi: {old_photo.path}")
            except Exception as e:
                print(f"Eski rasm o'chirishda xatolik: {e}")