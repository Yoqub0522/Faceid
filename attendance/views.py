# attendance/views.py (YANGILANGAN)
import os
import base64
import numpy as np
import cv2
import threading
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from deepface import DeepFace
import json

from .models import Employee, FaceEncoding, Attendance
from .forms import EmployeeForm, AttendanceFilterForm

# Logger sozlash
logger = logging.getLogger(__name__)


# DeepFace modelini oldindan yuklash
def preload_deepface():
    try:
        logger.info("🔄 DeepFace VGG-Face modelini yuklash...")
        DeepFace.build_model("VGG-Face")
        logger.info("✅ DeepFace modeli tayyor")
    except Exception as e:
        logger.error(f"❌ DeepFace modelini yuklashda xatolik: {e}")


# Modelni background threadda yuklash
if not hasattr(settings, 'DEEPFACE_LOADED'):
    threading.Thread(target=preload_deepface, daemon=True).start()
    settings.DEEPFACE_LOADED = True


@require_http_methods(["GET"])
def index(request):
    """Bosh sahifa - faol xodimlar ro'yxati"""
    employees = Employee.objects.filter(is_active=True).select_related().order_by('full_name')
    today = timezone.now().date()

    # Bugungi davomat statistikasi
    today_attendance = Attendance.objects.filter(date=today).select_related('employee')
    checked_in = today_attendance.filter(check_in__isnull=False).count()
    total_employees = employees.count()

    context = {
        'employees': employees,
        'stats': {
            'total': total_employees,
            'checked_in_today': checked_in,
            'remaining_today': total_employees - checked_in
        }
    }
    return render(request, 'attendance/index.html', context)


@require_http_methods(["GET", "POST"])
def enroll(request):
    """Yangi xodim qo'shish"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                employee = form.save()
                messages.success(request, f"{employee.full_name} muvaffaqiyatli qo'shildi!")
                logger.info(f"Yangi xodim qo'shildi: {employee.full_name} ({employee.email})")
                return redirect('attendance:enroll_images', employee_id=employee.id)
            except Exception as e:
                messages.error(request, f"Xodimni saqlashda xatolik: {str(e)}")
                logger.error(f"Xodimni saqlashda xatolik: {e}")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = EmployeeForm()

    return render(request, 'attendance/enroll.html', {'form': form})


@require_http_methods(["GET", "POST"])
def enroll_images(request, employee_id):
    """Xodimga yuz kodlarini qo'shish"""
    employee = get_object_or_404(Employee, id=employee_id, is_active=True)

    if request.method == 'POST':
        print(f"📸 POST so'rovi: {employee.full_name} uchun yuz qo'shilmoqda")
        img_b64 = request.POST.get('photo')

        if not img_b64:
            print("❌ Rasm topilmadi")
            return JsonResponse({'success': False, 'message': 'Rasm topilmadi'})

        try:
            # Base64 ni decode qilish
            if img_b64.startswith('data:'):
                header, encoded = img_b64.split(',', 1)
            else:
                encoded = img_b64

            print(f"📊 Rasm hajmi: {len(encoded)} belgi")
            img_bytes = base64.b64decode(encoded)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                print("❌ Rasm decode qilishda xatolik")
                return JsonResponse({'success': False, 'message': 'Rasmni decode qilishda xatolik'})

            print(f"🖼️ Rasm o'lchami: {img.shape}")

            # Yuz encoding olish
            print("🔍 Yuz encoding olinmoqda...")
            rep = DeepFace.represent(
                img_path=img,
                model_name='VGG-Face',
                enforce_detection=True,  # ✅ Yuz aniqlanishi shart
                detector_backend='opencv'
            )

            if not rep:
                print("❌ Yuz aniqlanmadi")
                return JsonResponse(
                    {'success': False, 'message': 'Rasmda yuz aniqlanmadi. Yuz aniq ko\'rinadigan rasm ishlating.'})

            encoding = np.array(rep[0]['embedding']).tolist()
            print(f"✅ Encoding olindi: {len(encoding)} o'lcham")

            # Encoding saqlash
            is_primary = not FaceEncoding.objects.filter(employee=employee).exists()
            face_encoding = FaceEncoding.objects.create(
                employee=employee,
                encoding=encoding,
                is_primary=is_primary
            )

            print(f"💾 Encoding saqlandi: {face_encoding.id}")
            return JsonResponse({
                'success': True,
                'message': f'Yuz kodi muvaffaqiyatli saqlandi! ({len(encoding)} o\'lcham)'
            })

        except Exception as e:
            print(f"❌ Xatolik: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Xatolik: {str(e)}'})

    # GET so'rovi
    encodings = employee.encodings.all()
    print(f"📋 GET so'rovi: {encodings.count()} ta encoding")
    return render(request, 'attendance/enroll_images.html', {
        'employee': employee,
        'encodings': encodings
    })

@require_http_methods(["GET"])
def capture_page(request):
    """Real-time yuz tanish sahifasi"""
    return render(request, 'attendance/capture.html')


@csrf_exempt
@require_http_methods(["POST"])
def recognize_api(request):
    """
    Real-time yuzni tanish API
    """
    start_time = datetime.now()

    # Tezlik cheklovi (daqiqaiga 10 so'rov)
    cache_key = f"rate_limit:{request.META.get('REMOTE_ADDR', 'unknown')}"
    # Soddalik uchun rate limit o'tkazib yuboriladi

    img_b64 = request.POST.get('image')
    if not img_b64:
        logger.warning("API: Rasm topilmadi")
        return JsonResponse({
            'status': 'error',
            'message': 'Rasm topilmadi'
        }, status=400)

    try:
        # Base64 decode
        if img_b64.startswith('data:'):
            header, encoded = img_b64.split(',', 1)
        else:
            encoded = img_b64

        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("API: Rasm decode qilishda xatolik")
            return JsonResponse({
                'status': 'error',
                'message': 'Yaroqsiz rasm formati'
            }, status=400)

        # Yuz encoding olish
        rep = DeepFace.represent(
            img_path=img,
            model_name='VGG-Face',
            enforce_detection=False,
            detector_backend='opencv'
        )

        if not rep or 'embedding' not in rep[0]:
            logger.warning("API: Embedding topilmadi")
            return JsonResponse({
                'status': 'error',
                'message': 'Yuz xususiyatlari topilmadi'
            })

        unknown_enc = np.array(rep[0]['embedding'])

        # Ma'lumotlar bazasidagi encodinglar bilan solishtirish
        db_encodings = FaceEncoding.objects.select_related('employee').filter(
            employee__is_active=True
        )

        if not db_encodings.exists():
            logger.warning("API: Bazada encoding topilmadi")
            return JsonResponse({
                'status': 'error',
                'message': 'Tizimda xodimlar mavjud emas'
            })

        best_match = None
        best_dist = float('inf')
        threshold = getattr(settings, 'FACE_DISTANCE_THRESHOLD', 0.6)

        for fe in db_encodings:
            try:
                known = np.array(fe.encoding)
                dist = np.linalg.norm(known - unknown_enc)

                if dist < best_dist:
                    best_dist = dist
                    best_match = fe

                    # Agar juda yaqin bo'lsa, tezroq to'xtash
                    if dist < 0.3:
                        break

            except Exception as e:
                logger.warning(f"API: Encoding o'qishda xatolik: {e}")
                continue

        processing_time = (datetime.now() - start_time).total_seconds()

        if best_match and best_dist < threshold:
            emp = best_match.employee
            now = timezone.now()

            with transaction.atomic():
                # Attendance yozish
                attendance, created = Attendance.objects.select_for_update().get_or_create(
                    employee=emp,
                    date=now.date(),
                    defaults={'check_in': now}
                )

                if not created and not attendance.check_out:
                    attendance.check_out = now
                    attendance.save()
                    message = "check_out"
                    action = "Chiqish"
                elif created:
                    message = "check_in"
                    action = "Kirish"
                else:
                    message = "already_checked"
                    action = "Allaqachon yozilgan"

            logger.info(f"API: Match - {emp.full_name} | distance={best_dist:.3f} | action={action}")

            return JsonResponse({
                'status': 'success',
                'employee_name': emp.full_name,
                'employee_id': str(emp.id),
                'message': message,
                'action': action,
                'distance': round(float(best_dist), 3),
                'processing_time': round(processing_time, 2)
            })

        logger.info(f"API: No match | min_distance={best_dist:.3f} | time={processing_time:.2f}s")
        return JsonResponse({
            'status': 'no_match',
            'message': 'Tanishmadi',
            'min_distance': round(float(best_dist), 3),
            'threshold': threshold,
            'processing_time': round(processing_time, 2)
        })

    except Exception as e:
        logger.error(f"API: Xatolik: {str(e)}", exc_info=True)
        return JsonResponse({
            'status': 'error',
            'message': f'Server xatosi: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def report(request):
    """Davomat hisoboti"""
    form = AttendanceFilterForm(request.GET or None)
    attendances = Attendance.objects.select_related('employee').order_by('-date', '-check_in')

    # Filtrlash
    if form.is_valid():
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        employee = form.cleaned_data.get('employee')

        if date_from:
            attendances = attendances.filter(date__gte=date_from)
        if date_to:
            attendances = attendances.filter(date__lte=date_to)
        if employee:
            attendances = attendances.filter(employee=employee)

    # Pagination uchun
    attendances = attendances[:500]  # Oxirgi 500 ta yozuv

    context = {
        'attendances': attendances,
        'form': form,
        'total_count': attendances.count()
    }
    return render(request, 'attendance/report.html', context)


@require_http_methods(["POST"])
def delete_encoding(request, encoding_id):
    """Yuz encodingini o'chirish"""
    encoding = get_object_or_404(FaceEncoding, id=encoding_id)
    employee_id = encoding.employee.id
    encoding.delete()
    messages.success(request, "Yuz kodi muvaffaqiyatli o'chirildi")
    return redirect('attendance:enroll_images', employee_id=employee_id)


@require_http_methods(["POST"])
def set_primary_encoding(request, encoding_id):
    """Asosiy encodingni belgilash"""
    encoding = get_object_or_404(FaceEncoding, id=encoding_id)
    encoding.is_primary = True
    encoding.save()
    messages.success(request, "Asosiy encoding belgilandi")
    return redirect('attendance:enroll_images', employee_id=encoding.employee.id)