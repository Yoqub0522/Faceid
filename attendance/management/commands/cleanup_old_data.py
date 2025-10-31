# attendance/management/commands/cleanup_old_data.py (YANGI)
from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Attendance, FaceEncoding
from datetime import timedelta


class Command(BaseCommand):
    help = 'Eski maʼlumotlarni tozalash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Necha kundan oldingi maʼlumotlarni o‘chirish (default: 365)',
        )

    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)

        # Eski davomat yozuvlarini o'chirish
        old_attendances = Attendance.objects.filter(date__lt=cutoff_date.date())
        attendance_count = old_attendances.count()
        old_attendances.delete()

        # Bir xodimga tegishli ko'p encodinglarni kamaytirish
        from django.db.models import Count
        from django.db import transaction

        with transaction.atomic():
            employees_with_many_encodings = FaceEncoding.objects.values(
                'employee'
            ).annotate(
                count=Count('id')
            ).filter(count__gt=5)

            for emp in employees_with_many_encodings:
                # Har bir xodim uchun faqat 5 ta eng yangi encodingni saqlash
                encodings_to_keep = FaceEncoding.objects.filter(
                    employee_id=emp['employee']
                ).order_by('-created_at')[:5]

                FaceEncoding.objects.filter(
                    employee_id=emp['employee']
                ).exclude(
                    id__in=[e.id for e in encodings_to_keep]
                ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ {attendance_count} ta eski davomat yozuvi o‘chirildi. "
                f"Encodinglar optimallashtirildi."
            )
        )