from django import forms
from .models import TrainingType, Trainers
from datetime import date


class TrainingTypeForm(forms.ModelForm):
    class Meta:
        model = TrainingType
        fields = ['title', 'description']

    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) < 3:
            raise forms.ValidationError('Назва типу тренування повинна містити щонайменше 3 символи.')
        return title

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) < 10:
            raise forms.ValidationError('Опис повинен містити щонайменше 10 символів.')
        return description


class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainers
        fields = [
            'first_name', 'last_name', 'birth', 'gender', 'phone',
            'qualification', 'specialization', 'bio', 'photo', 'client_qty_constraint'
        ]
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 5}),
        }


    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.startswith('+'):
            phone = '+' + phone
        return phone

    def clean_birth(self):
        birth = self.cleaned_data['birth']
        today = date.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        if age < 18:
            raise forms.ValidationError('Тренер повинен бути старше 18 років.')
        return birth

    def clean_client_qty_constraint(self):
        client_qty = self.cleaned_data['client_qty_constraint']
        if client_qty < 0:
            raise forms.ValidationError('Кількість клієнтів не може бути від’ємною.')
        return client_qty