from django import forms
from django.db import models
from django.forms import modelformset_factory
from .models import Match, Sports, ScheduledMatches, MatchDay
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from crispy_forms.helper import FormHelper, Layout


class RegistrationForm(forms.ModelForm):

    phone = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['confirm_password'].label = 'Подтвердите пароль'
        self.fields['phone'].label = 'Номер телефона'
        self.fields['email'].label = 'Email'

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists() and self.cleaned_data['email'] != '':
            raise forms.ValidationError('Данный Email уже зарегистрирован')
        return email

    def clean_username(self):

        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с данным именем уже зарегистрирован')
        return username

    def clean(self):

        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']

        if password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'email', 'phone']


class LoginForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        """if not User.objects.filter(username=username).exists():
            raise forms.ValidationError(f'Пользователь с логином {username} не зарегистрирован')"""
        user = User.objects.filter(username=username).first()
        if user:
            """if not user.check_password(password):
                raise forms.ValidationError(f'Неверный пароль')"""

        return self.cleaned_data

    class Meta:

        model = User
        fields = ['username', 'password']


class SquadForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["red_squad", "blue_squad"]


class ScheduleForm(forms.ModelForm):

    class Meta:
        model = ScheduledMatches

        fields = ["date", "time", "red_team", "blue_team"]

        widgets = {
            'date': forms.DateInput(
                format='%d/%m/%Y',
                attrs={'class': 'form-control',
                       'placeholder': 'Выберите дату',
                       'type': 'date'  # <--- IF I REMOVE THIS LINE, THE INITIAL VALUE IS DISPLAYED
                       }),
            "time": forms.TimeInput(
                attrs={'placeholder': "Формат 12:00"}
            )
        }

        def clean_date(self):
            date = self.cleaned_data['date']
            if date < datetime.date.today():
                raise forms.ValidationError("The date cannot be in the past!")
            return date


class SendScore(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    class Meta:
        model = Match
        fields = '__all__'


ScheduleFormSet = modelformset_factory(ScheduledMatches, form=ScheduleForm, extra=10)


class ScheduleFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ScheduleFormSetHelper, self).__init__(*args, **kwargs)
        self.layout = Layout(
            'date',
            'time',
            'red_team',
            'blue_team'
        )
        self.render_required_fields = True
        self.form_method = "POST"
        # self.template = "schedule_match.html"
