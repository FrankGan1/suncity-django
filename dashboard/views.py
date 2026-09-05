from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings

from accounts.forms import AdminAddClientForm
from accounts.models import Client
from accounts.views import _send_password_reset_email

User = get_user_model()


@staff_member_required
def dashboard_home(request):
    query = request.GET.get('q', '').strip()
    clients = Client.objects.select_related('user').all()
    if query:
        clients = clients.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(user__email__icontains=query)
            | Q(phone_number__icontains=query)
        )

    context = {
        'clients': clients,
        'query': query,
        'total_clients': Client.objects.count(),
        'active_clients': Client.objects.filter(user__is_active=True).count(),
    }
    return render(request, 'dashboard/home.html', context)


@staff_member_required
def add_client(request):
    if request.method == 'POST':
        form = AdminAddClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client "{client.full_name}" was added successfully.')
            return redirect('dashboard:home')
    else:
        form = AdminAddClientForm()

    return render(request, 'dashboard/add_client.html', {'form': form})


@staff_member_required
def delete_client(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if request.method == 'POST':
        name = client.full_name
        user = client.user
        client.delete()
        user.delete()
        messages.success(request, f'Client "{name}" was deleted.')
        return redirect('dashboard:home')

    return render(request, 'dashboard/confirm_delete.html', {'client': client})


@staff_member_required
def send_reset_password(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if request.method == 'POST':
        reset_url = _send_password_reset_email(request, client.user)
        if 'console' in settings.EMAIL_BACKEND:
            messages.success(
                request,
                f'Password reset link generated for {client.email} '
                f'(console email backend — link: {reset_url}).',
            )
        else:
            messages.success(request, f'Password reset email sent to {client.email}.')
        return redirect('dashboard:home')

    return render(request, 'dashboard/confirm_reset.html', {'client': client})
