from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings

from .forms import (
    ClientRegisterForm, EmailAuthenticationForm, ForgotPasswordForm, SetNewPasswordForm,
)

User = get_user_model()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:post_login_redirect')

    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, 'Account created successfully. Please sign in.')
            return redirect('accounts:login')
    else:
        form = ClientRegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:post_login_redirect')

    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)  # expires when browser closes
            return redirect('accounts:post_login_redirect')
    else:
        form = EmailAuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('core:home')


@login_required
def post_login_redirect(request):
    if request.user.is_staff:
        return redirect('dashboard:home')
    return redirect('accounts:my_account')


@login_required
def my_account_view(request):
    client = getattr(request.user, 'client_profile', None)
    return render(request, 'accounts/my_account.html', {'client': client})


def _send_password_reset_email(request, user):
    """Shared helper used both by the public 'forgot password' page and
    by the admin dashboard's 'Send Reset Password' action."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_path = reverse('accounts:reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
    reset_url = request.build_absolute_uri(reset_path)

    subject = f'{settings.SITE_NAME} — Reset your password'
    message = render_to_string('accounts/emails/password_reset_email.txt', {
        'user': user,
        'reset_url': reset_url,
        'site_name': settings.SITE_NAME,
    })
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    return reset_url


def forgot_password_view(request):
    sent = False
    reset_url_preview = None  # shown only when using the console/dev email backend

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email__iexact=email, is_active=True).first()
            if user:
                reset_url_preview = _send_password_reset_email(request, user)
            # Always show the same success message — don't reveal whether
            # the email exists in the system.
            sent = True
    else:
        form = ForgotPasswordForm()

    show_preview = sent and reset_url_preview and 'console' in settings.EMAIL_BACKEND
    return render(request, 'accounts/forgot_password.html', {
        'form': form,
        'sent': sent,
        'reset_url_preview': reset_url_preview if show_preview else None,
    })


def reset_password_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    valid_link = user is not None and default_token_generator.check_token(user, token)

    if not valid_link:
        return render(request, 'accounts/reset_password_confirm.html', {'valid_link': False})

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, 'Your password has been reset. Please sign in.')
            return redirect('accounts:login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'accounts/reset_password_confirm.html', {
        'valid_link': True, 'form': form,
    })
