from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrateur'
        AGENT = 'agent', 'Agent de support'
        CLIENT = 'client', 'Client'

    phone = models.CharField(max_length=20, blank=True, verbose_name='Numéro')
    address = models.TextField(blank=True, verbose_name='Adresse')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT, verbose_name='Role')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',
        related_query_name='user',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',
        related_query_name='user',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.username

    @property
    def is_support_admin(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_support_agent(self):
        return self.is_staff or self.role in {self.Role.ADMIN, self.Role.AGENT}
