# attendance/admin.py (YANGILANGAN)
from django.contrib import admin
from .models import Employee, FaceEncoding, Attendance


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'position', 'is_active', 'created_at','id',]
    list_filter = ['is_active', 'position', 'created_at']
    search_fields = ['full_name', 'email', 'position']
    readonly_fields = ['created_at']
    list_per_page = 20


@admin.register(FaceEncoding)
class FaceEncodingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['employee__full_name']
    readonly_fields = ['created_at']
    list_per_page = 20


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'duration']
    list_filter = ['date', 'employee']
    search_fields = ['employee__full_name']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    list_per_page = 50

    def duration(self, obj):
        return obj.duration()

    duration.short_description = 'Davomiylik (soat)'