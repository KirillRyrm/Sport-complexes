from django import forms
from .models import Client
from django.core.validators import RegexValidator, MinValueValidator
from gym_app.models import Subscription

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'email', 'phone', 'birth', 'gender']
        widgets = {
            'birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=Client.GENDER_CHOICES),
        }
        labels = {
            'first_name': 'Ім’я',
            'last_name': 'Прізвище',
            'email': 'Email',
            'phone': 'Телефон',
            'birth': 'Дата народження',
            'gender': 'Стать',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})



class BalanceTopUpForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        label='Сума поповнення (грн)',
        validators=[MinValueValidator(0.01, message='Сума повинна бути більше 0.')],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'})
    )


class PurchaseSubscriptionForm(forms.Form):
    subscription = forms.ModelChoiceField(
        queryset=Subscription.objects.all(),
        label='Абонемент',
        empty_label='Виберіть абонемент'
    )