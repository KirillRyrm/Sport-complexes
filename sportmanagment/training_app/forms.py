from django import forms
from .models import TrainingType, Trainers, TrainingSessions
from gym_app.models import Gym
from datetime import date, datetime


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


class TrainingSessionForm(forms.ModelForm):
    gym = forms.ModelChoiceField(queryset=Gym.objects.all(), label='Зал', empty_label='Виберіть зал')

    class Meta:
        model = TrainingSessions
        fields = ['session_date', 'start_time', 'end_time', 'max_participants', 'training_type', 'gym', 'location', 'status']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'training_type': forms.Select(),
            'location': forms.Select(),
            'status': forms.Select(),
        }

    def clean_session_date(self):
        session_date = self.cleaned_data['session_date']
        today = datetime.now().date()
        if session_date.date() < today:
            raise forms.ValidationError('Дата сесії не може бути в минулому.')
        return session_date


    def clean_end_time(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('Час початку повинен бути раніше часу закінчення.')

        session_date = self.cleaned_data['session_date']

        if session_date and start_time:
            # Составляем datetime для начала тренировки
            session_start = datetime.combine(session_date, start_time)

            # Получаем текущее время
            now = datetime.now()

            if session_start < now:
                raise forms.ValidationError('Дата и время тренировки не могут быть в прошлом.')
        return end_time


class ClientAttendanceForm(forms.Form):
    trainer = forms.ModelChoiceField(
        queryset=Trainers.objects.all(),
        required=False,
        label='Тренер',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    training_type = forms.ModelChoiceField(
        queryset=TrainingType.objects.all(),
        required=False,
        label='Тип тренування',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        label='Дата початку',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        label='Дата закінчення',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class TrainingTypeRankingForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        label='Дата початку',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        label='Дата закінчення',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )


class LocationRankingForm(forms.Form):
    start_date = forms.DateField(
        required=False,
        label='Дата початку',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        label='Дата закінчення',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )