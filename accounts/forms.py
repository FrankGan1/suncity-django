from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import Client

User = get_user_model()


BASE_WIDGET_ATTRS = {'class': 'form-input'}


class ClientRegisterForm(forms.Form):
    """Public sign-up form for new clients."""

    full_name = forms.CharField(
        label='Full Name',
        max_length=150,
        widget=forms.TextInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': 'John Doe'}),
    )
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': 'you@example.com'}),
    )
    phone_number = forms.CharField(
        label='Phone Number',
        max_length=30,
        widget=forms.TextInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '+254 700 000 000'}),
    )
    address = forms.CharField(
        label='Address',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '123 Main Street, City'}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '••••••••'}),
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '••••••••'}),
    )
    agree_terms = forms.BooleanField(
        label='I agree to the Terms of Service and Privacy Policy',
        required=True,
        error_messages={'required': 'You must agree to the Terms of Service and Privacy Policy.'},
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get('password')
        confirm_password = cleaned.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
        )
        first_name, _, last_name = data['full_name'].partition(' ')
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        client = Client.objects.create(
            user=user,
            phone_number=data['phone_number'],
            address=data.get('address', ''),
        )
        return client


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that labels the identity field as 'Email Address'."""

    username = forms.CharField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            **BASE_WIDGET_ATTRS, 'placeholder': 'you@example.com', 'autofocus': True,
        }),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '••••••••'}),
    )
    remember_me = forms.BooleanField(required=False, initial=False)

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Please enter a correct email and password.',
    }


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': 'name@company.com'}),
    )


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '••••••••'}),
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '••••••••'}),
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned


class AdminAddClientForm(forms.Form):
    """Used by staff/admin in the dashboard to add a client manually."""

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': 'John Doe'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': 'you@example.com'}),
    )
    phone_number = forms.CharField(
        max_length=30, required=False,
        widget=forms.TextInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '+254 700 000 000'}),
    )
    address = forms.CharField(
        max_length=255, required=False,
        widget=forms.TextInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': '123 Main Street, City'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={**BASE_WIDGET_ATTRS, 'placeholder': 'Temporary password'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A client with this email already exists.')
        return email

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            password=data['password'],
        )
        first_name, _, last_name = data['full_name'].partition(' ')
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        return Client.objects.create(
            user=user,
            phone_number=data.get('phone_number', ''),
            address=data.get('address', ''),
        )
