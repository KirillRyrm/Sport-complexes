from .models import Gym, Equipment
from django import forms

class GymForm(forms.ModelForm):
    class Meta:
        model = Gym
        fields = ['gym_name', 'address', 'phone', 'email']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.startswith('+') or not phone[1:].isdigit():
            raise forms.ValidationError('Телефон повинен починатися з "+" і містити лише цифри.')
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if '@' not in email:
            raise forms.ValidationError('Введіть коректну email-адресу.')
        return email

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['equipment_name', 'description']

    def clean_equipment_name(self):
        equipment_name = self.cleaned_data['equipment_name']
        if len(equipment_name) < 3:
            raise forms.ValidationError('Назва обладнання повинна містити щонайменше 3 символи.')
        return equipment_name