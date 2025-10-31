# attendance/models.py (YANGILANGAN)
import uuid
from django.db import models
from django.core.exceptions import ValidationError
import os


def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB
        raise ValidationError("Rasm hajmi 5MB dan oshmasligi kerak")


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200, verbose_name="To'liq ism")
    email = models.EmailField(unique=True, verbose_name="Email",blank=True,null=True)
    position = models.CharField(max_length=120, blank=True, verbose_name="Lavozim")
    photo = models.ImageField(
        upload_to='employees/',
        null=True,
        blank=True,
        validators=[validate_image_size],
        verbose_name="Rasm"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def delete(self, *args, **kwargs):
        if self.photo:
            if os.path.isfile(self.photo.path):
                os.remove(self.photo.path)
        super().delete(*args, **kwargs)


class FaceEncoding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='encodings'
    )
    encoding = models.JSONField(verbose_name="Yuz kodi")
    created_at = models.DateTimeField(auto_now_add=True)
    is_primary = models.BooleanField(default=False, verbose_name="Asosiy encoding")

    class Meta:
        verbose_name = "Yuz kodi"
        verbose_name_plural = "Yuz kodlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Boshqa primary encodinglarni false qilish
            FaceEncoding.objects.filter(
                employee=self.employee,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(verbose_name="Sana")
    check_in = models.DateTimeField(null=True, blank=True, verbose_name="Kirish vaqti")
    check_out = models.DateTimeField(null=True, blank=True, verbose_name="Chiqish vaqti")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomatlar"
        unique_together = ('employee', 'date')
        ordering = ['-date', '-check_in']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    def duration(self):
        """Ishlash davomiyligini hisoblash"""
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            hours = delta.total_seconds() / 3600
            return round(hours, 2)
        return 0

    def clean(self):
        if self.check_out and self.check_in and self.check_out <= self.check_in:
            raise ValidationError("Chiqish vaqti kirish vaqtidan keyin bo'lishi kerak")