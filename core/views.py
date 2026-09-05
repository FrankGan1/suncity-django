from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import ContactForm


def home_view(request):
    return render(request, 'core/home.html')


def services_view(request):
    return render(request, 'core/services.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                send_mail(
                    subject=f"New contact message from {data['name']}",
                    message=f"From: {data['name']} <{data['email']}>\n\n{data['message']}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Thanks! We've received your message and will get back to you shortly.")
            return redirect('core:contact')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})
