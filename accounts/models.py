from django.conf import settings
from django.db import models


class Client(models.Model):
    """
    Extra profile information for a signed-up client.
    Every Client wraps a standard Django auth User (used for login,
    passwords, and the built-in password-reset machinery).

    Staff/admin users (is_staff=True) do NOT get a Client record — they
    manage clients from the /dashboard/ area instead.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_profile',
    )
    phone_number = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def email(self):
        return self.user.email

    @property
    def is_active(self):
        return self.user.is_active
