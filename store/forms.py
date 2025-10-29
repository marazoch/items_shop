from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")  # пароль1/пароль2 уже внутри UserCreationForm

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip()
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    login = forms.CharField(label="Логин или email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    error_messages = {
        "invalid_login": "Неверные логин/email или пароль.",
        "inactive": "Учетная запись отключена.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        login = cleaned.get("login", "").strip()
        password = cleaned.get("password", "")

        if login and password:
            user = User.objects.filter(
                Q(username__iexact=login) | Q(email__iexact=login)
            ).first()

            if user is None or not user.check_password(password):
                raise forms.ValidationError(self.error_messages["invalid_login"])
            if not user.is_active:
                raise forms.ValidationError(self.error_messages["inactive"])

            self.user_cache = user
        return cleaned

    def get_user(self):
        return self.user_cache