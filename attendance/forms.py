# attendance/forms.py (YANGILANGAN)
from django import forms
from .models import Employee, FaceEncoding
import re


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['full_name', 'email', 'position', 'photo']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Toʻliq ism kiriting'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com (ixtiyoriy)'  # ✅ Ixtiyoriy ekanligini ko'rsatamiz
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lavozimi'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        labels = {
            'full_name': 'Toʻliq Ism *',
            'email': 'Email (ixtiyoriy)',  # ✅ Ixtiyoriy ekanligini ko'rsatamiz
            'position': 'Lavozim',
            'photo': 'Rasm'
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if len(full_name.strip()) < 3:
            raise forms.ValidationError("Ism kamida 3 ta belgidan iborat boʻlishi kerak")
        return full_name.strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # ✅ EMAIL BO'SH BO'LSA, TEKSHIRMASDAN QAYTARAMIZ
        if not email or email.strip() == '':
            return None  # yoki return '' - model blank=True, null=True qo'llab-quvvatlaydi

        # ✅ Faqat email mavjud bo'lganda unique tekshiramiz
        if Employee.objects.filter(email=email).exists():
            if self.instance and self.instance.pk:
                # Yangilash holati
                if Employee.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError("Bu email allaqachon roʻyxatdan oʻtgan")
            else:
                # Yangi yaratish holati
                raise forms.ValidationError("Bu email allaqachon roʻyxatdan oʻtgan")
        return email

class FaceEncodingForm(forms.ModelForm):
    class Meta:
        model = FaceEncoding
        fields = ['is_primary']
        widgets = {
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'is_primary': 'Asosiy encoding sifatida belgilash'
        }

class AttendanceFilterForm(forms.Form):
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Dan'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Gacha'
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Xodim'
    )